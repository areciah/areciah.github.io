"""Build-time import, run from the root of a fresh checkout."""
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
                "permalink": destination, "render_with_liquid": False}
    content = api(f"pages/{page_id}/markdown?markdown_version=v2")
    if content.get("truncated"):
        raise ValueError(f"Incomplete Notion page: {page_id}")
    body = re.sub(r"""https://[^\s<>"')]+""", store_attachment, content["markdown"])
    header = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items())
    Path(f"_posts/{day}-notion-{page_id}.md").write_text(f"---\n{header}\n---\n\n{body}\n", encoding="utf-8")

    redirects = Path("redirects")
    redirects.mkdir(exist_ok=True)
    (redirects / f"notion-{page_id}.html").write_text(
        f"---\nlayout: post-redirect\npermalink: /posts/{page_id}/\ndestination: {destination}\n---\n",
        encoding="utf-8")


def main():
    if not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_DATA_SOURCE_ID"):
        raise SystemExit("Set the NOTION_TOKEN secret and NOTION_DATA_SOURCE_ID variable.")
    source = UUID(os.environ["NOTION_DATA_SOURCE_ID"]).hex
    query = {"filter": {"property": "상태", "status": {"equals": "발행"}}}
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
