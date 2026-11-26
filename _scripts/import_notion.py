"""Build-time import, run from the root of a fresh checkout."""
import base64
import hashlib
import json
import os
import re
import shutil
import time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import UUID


def api(path, body=None):
    request = Request("https://api.notion.com/v1/" + path,
                      data=json.dumps(body).encode() if body else None,
                      headers={"Authorization": "Bearer " + os.environ["NOTION_TOKEN"],
                               "Notion-Version": "2026-03-11",
                               "Content-Type": "application/json"})
    for attempt in range(5):
        try:
            with urlopen(request, timeout=45) as response:
                return json.load(response)
        except HTTPError as error:
            if attempt == 4 or error.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(int(error.headers.get("Retry-After", 2 ** attempt)))


def store_attachment(match):
    url = match.group()
    parts = urlsplit(url)
    if not (parts.hostname or "").endswith(".amazonaws.com") or "x-amz-signature=" not in parts.query.lower():
        return url
    name = hashlib.sha256(parts.path.encode()).hexdigest()[:24]
    suffix = Path(parts.path).suffix.lower()
    asset = Path("assets/notion") / (name + (suffix if re.fullmatch(r"\.[a-z0-9]{1,8}", suffix) else ""))
    asset.parent.mkdir(parents=True, exist_ok=True)
    if not asset.exists():
        with urlopen(url, timeout=60) as response, asset.open("wb") as output:
            shutil.copyfileobj(response, output)
    return "/" + asset.as_posix()


def plain(items):
    return "".join(item["plain_text"] for item in items)


LOCKED = "발행 (비밀번호)"


def encrypt_article(markdown, password):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from markdown_it import MarkdownIt
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound

    def highlight_fence(code, language, attributes):
        if not language or language.lower() in {"text", "txt", "plaintext", "output", "console"}:
            return ""  # MarkdownIt escapes and renders plain text.
        try:
            lexer = get_lexer_by_name(language.lower(), stripnl=False, ensurenl=False)
        except ClassNotFound:
            return ""
        tokens = highlight(code, lexer, HtmlFormatter(nowrap=True))
        return f'<span class="highlight">{tokens}</span>'


    salt, nonce = os.urandom(16), os.urandom(12)
    iterations = 600_000
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations, dklen=32)
    html = MarkdownIt("commonmark", {"html": False, "highlight": highlight_fence}).enable("table").render(markdown)
    encrypted = AESGCM(key).encrypt(nonce, html.encode(), None)
    return {"iterations": iterations, **{
        name: base64.b64encode(value).decode("ascii")
        for name, value in (("salt", salt), ("nonce", nonce), ("ciphertext", encrypted))
    }}


def export(page):
    props = page["properties"]
    title = next(p["title"] for p in props.values() if p["type"] == "title")
    published = props.get("발행일", {}).get("date") or {}
    day = date.fromisoformat(published.get("start", page["created_time"])[:10])
    category = props.get("카테고리", {})
    choices = category.get("multi_select", []) or [category.get("select")]
    page_id = UUID(page["id"]).hex
    address = plain(props.get("주소", {}).get("rich_text", [])) or plain(title)
    slug = re.sub(r"[\W_]+", "-", address.casefold()).strip("-")[:60].rstrip("-") or "note"
    destination = f"/posts/{slug}-{page_id[:12]}/"
    metadata = {"layout": "post", "title": plain(title), "date": str(day),
                "description": plain(props.get("요약", {}).get("rich_text", [])),
                "categories": [c["name"] for c in choices if c],
                "tags": [tag["name"] for tag in props.get("태그", {}).get("multi_select", [])],
                "permalink": destination, "render_with_liquid": False}
    content = api(f"pages/{page_id}/markdown?markdown_version=v2")
    if content.get("truncated"):
        raise ValueError(f"Incomplete Notion page: {page_id}")
    password = plain(props.get("글 비밀번호", {}).get("rich_text", []))
    protected = props.get("상태", {}).get("status", {}).get("name") == LOCKED
    if protected or password:
        if not protected or not password.strip():
            raise SystemExit(f"글 {page_id}: 잠금 발행에는 '발행 (비밀번호)' 상태와 글 비밀번호가 모두 필요합니다.")
        metadata.update(layout="locked-post", locked=True, description="", tags=[], categories=[],
                        payload=encrypt_article(content["markdown"], password))
        body = ""
    else:
        project = (props.get("프로젝트", {}).get("select") or {}).get("name")
        if project:
            metadata["project"] = project
        body = re.sub(r"""https://[^\s<>"')]+""", store_attachment, content["markdown"])
    header = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items())
    Path("_posts").mkdir(exist_ok=True)
    Path(f"_posts/{day}-notion-{page_id}.md").write_text(f"---\n{header}\n---\n\n{body}\n", encoding="utf-8")

    redirects = Path("redirects")
    redirects.mkdir(exist_ok=True)
    (redirects / f"notion-{page_id}.html").write_text(
        f"---\nlayout: post-redirect\npermalink: /posts/{page_id}/\ndestination: {destination}\n---\n",
        encoding="utf-8")


def resolve_source(configured_id):
    try:
        object_id = UUID(configured_id.strip()).hex
    except ValueError:
        raise SystemExit("DATABASE_ID에는 Notion 데이터베이스 또는 데이터 소스의 UUID를 입력하세요.") from None

    try:
        database = api(f"databases/{object_id}")
    except HTTPError as error:
        if error.code != 404:
            raise
    else:
        sources = database["data_sources"]
        if len(sources) != 1:
            raise SystemExit("DATABASE_ID에 발행할 데이터 소스의 ID를 지정하세요.")
        return sources[0]["id"]

    try:
        return api(f"data_sources/{object_id}")["id"]
    except HTTPError as error:
        if error.code != 404:
            raise
        raise SystemExit(
            "Notion 404: DATABASE_ID와 데이터베이스 접근 권한을 확인하세요. "
            "뷰 ID(?v=)가 아닌 데이터베이스 ID를 입력하고, 데이터베이스의 연결 메뉴에 "
            "NOTION_TOKEN을 발급한 통합을 추가하세요."
        ) from None


def main():
    if not os.getenv("NOTION_TOKEN") or not os.getenv("DATABASE_ID"):
        raise SystemExit("Set the NOTION_TOKEN and DATABASE_ID repository secrets.")
    source = resolve_source(os.environ["DATABASE_ID"])
    query = {"filter": {"or": [{"property": "상태", "status": {"equals": state}}
                               for state in ("발행", LOCKED)]}}
    count = 0
    while True:
        result = api(f"data_sources/{source}/query", query)
        for page in result["results"]:
            export(page)
            count += 1
        if not result["has_more"]:
            break
        query["start_cursor"] = result["next_cursor"]
    print(f"Imported {count} published Notion posts.")


if __name__ == "__main__":
    main()
