"""Build-time import, run from the root of a fresh checkout."""
import base64
import hashlib
import html as html_entities
import mimetypes
import json
import os
import re
import shutil
import time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
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


def notion_image_url(url):
    parts = urlsplit(url)
    host = parts.hostname or ""
    return parts.scheme == "https" and host.endswith(
        (".amazonaws.com", ".notion.so", ".notion.com", ".notionusercontent.com")
    )


class ImageRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not notion_image_url(newurl):
            raise ValueError("Notion 사진의 리디렉션 주소를 확인하세요.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def embed_notion_image(url):
    # No Notion token or signed URL is written to the page or build log.
    try:
        with build_opener(ImageRedirect()).open(url, timeout=60) as response:
            mime = response.headers.get_content_type()
            if mime == "application/octet-stream":
                mime = mimetypes.guess_type(urlsplit(url).path)[0] or mime
            if not mime.startswith("image/"):
                raise ValueError("Notion 사진 주소에서 이미지가 반환되지 않았습니다.")
            data = response.read()
    except OSError:
        raise ValueError("Notion 사진을 내려받지 못했습니다. 파일 접근 권한을 확인하고 다시 빌드하세요.") from None
    if not data:
        raise ValueError("빈 Notion 사진을 받았습니다.")
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def notion_image_tag(state, silent):
    # Notion v2 also uses this form for images with block attributes.
    match = re.match(r'<image\s+([^>]+)>(.*?)</image>', state.src[state.pos:], re.S)
    if not match:
        return False
    source = re.search(r'(?:^|\s)source="([^"]+)"', match[1])
    if not source:
        return False
    url = html_entities.unescape(source[1])
    if not state.md.validateLink(url):
        return False
    if not silent:
        token = state.push("image", "img", 0)
        token.attrSet("src", url)
        token.children = state.md.parseInline(html_entities.unescape(match[2]), state.env)[0].children
    state.pos += match.end()
    return True


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
    parser = MarkdownIt("commonmark", {"html": False, "highlight": highlight_fence}).enable("table")
    parser.inline.ruler.before("html_inline", "notion_image", notion_image_tag)
    image_cache = {}
    render_image = parser.renderer.rules["image"]

    def private_image(tokens, idx, options, env):
        token = tokens[idx]
        url = token.attrGet("src")
        if notion_image_url(url):
            if url not in image_cache:
                image_cache[url] = embed_notion_image(url)
            token.attrSet("src", image_cache[url])
        return render_image(tokens, idx, options, env)

    parser.renderer.rules["image"] = private_image
    html = parser.render(markdown)
    encrypted = AESGCM(key).encrypt(nonce, html.encode(), None)
    return {"iterations": iterations, **{
        name: base64.b64encode(value).decode("ascii")
        for name, value in (("salt", salt), ("nonce", nonce), ("ciphertext", encrypted))
    }}


def read_body(page_id):
    content = api(f"pages/{page_id}/markdown?markdown_version=v2")
    if content.get("truncated"):
        raise ValueError(f"Incomplete Notion page: {page_id}")
    return content["markdown"]


def public_body(markdown):
    return re.sub(r"""https://[^\s<>"')]+""", store_attachment, markdown)


def rich(props, name):
    return plain(props.get(name, {}).get("rich_text", []))


def write_profile(title, summary, markdown):
    intro, *parts = re.split(r"^## (.+?)\s*$", markdown, flags=re.M)
    sections = []
    awards = []
    for heading, body in zip(parts[::2], parts[1::2]):
        anchor = "awards" if heading == "수상 내역" else f"section-{len(sections) + 1}"
        sections.append({"title": heading, "id": anchor, "body": body.strip()})
        if anchor == "awards":
            awards = [line[2:] for line in body.splitlines() if line.startswith(("- ", "* "))]
    profile = {"name": title, "headline": summary, "intro": intro.strip(),
               "sections": sections, "awards": awards}
    Path("_data").mkdir(exist_ok=True)
    Path("_data/cv.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_project(page, used):
    props = page["properties"]
    slug = rich(props, "주소").strip() or UUID(page["id"]).hex
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in used:
        raise ValueError(f"프로젝트 주소 형식 또는 중복 확인: {page['id']}")
    used.add(slug)
    title = next(plain(p["title"]) for p in props.values() if p["type"] == "title")
    meta = {"title": title, "topic": rich(props, "주제"), "role": rich(props, "맡은 역할"),
            "description": rich(props, "요약"), "render_with_liquid": False}
    header = "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in meta.items())
    path = Path("_projects", slug + ".md")
    if path.exists():
        raise ValueError(f"기존 프로젝트와 주소가 겹칩니다: {slug}")
    body = public_body(read_body(page["id"]))
    path.write_text(f"---\nnotion_managed: true\n{header}\n---\n\n{body}\n", encoding="utf-8")


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
    markdown = read_body(page_id)
    password = plain(props.get("글 비밀번호", {}).get("rich_text", []))
    protected = props.get("상태", {}).get("status", {}).get("name") == LOCKED
    if protected or password:
        if not protected or not password.strip():
            raise SystemExit(f"글 {page_id}: 잠금 발행에는 '발행 (비밀번호)' 상태와 글 비밀번호가 모두 필요합니다.")
        metadata.update(layout="locked-post", locked=True, description="", tags=[], categories=[],
                        payload=encrypt_article(markdown, password))
        body = ""
    else:
        project = (props.get("프로젝트", {}).get("select") or {}).get("name")
        if project:
            metadata["project"] = project
        body = public_body(markdown)
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
                               for state in ("발행", LOCKED, "프로젝트 공개", "소개 반영")]}}
    for path in Path("_projects").glob("*.md"):
        if path.read_text(encoding="utf-8").startswith("---\nnotion_managed: true\n"):
            path.unlink()
    used = set()
    profile_seen = False
    count = 0
    while True:
        result = api(f"data_sources/{source}/query", query)
        for page in result["results"]:
            props = page["properties"]
            state = props["상태"]["status"]["name"]
            if state == "프로젝트 공개":
                export_project(page, used)
            elif state == "소개 반영":
                if profile_seen:
                    raise ValueError("소개 반영 상태의 페이지는 하나만 지정하세요.")
                title = next(plain(p["title"]) for p in props.values() if p["type"] == "title")
                write_profile(title, rich(props, "요약"), public_body(read_body(page["id"])))
                profile_seen = True
            else:
                export(page)
                count += 1
        if not result["has_more"]:
            break
        query["start_cursor"] = result["next_cursor"]
    if not profile_seen:
        write_profile("arecia", "", "")
    print(f"Imported {count} published Notion posts.")


if __name__ == "__main__":
    main()
