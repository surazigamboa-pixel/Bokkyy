import httpx
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from models import BookResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE, USER_AGENT
from utils import normalize

SOURCE = "Standard Ebooks"
FEED = "https://standardebooks.org/opds/all"

async def search(query: str):
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = await client.get(FEED)
        resp.raise_for_status()
    root = ET.fromstring(resp.content)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    q = normalize(query)
    results = []
    for entry in root.findall("a:entry", ns):
        title = entry.findtext("a:title", default="", namespaces=ns)
        author = entry.findtext("a:author/a:name", default="Autor desconocido", namespaces=ns)
        summary = entry.findtext("a:summary", default=None, namespaces=ns)
        if q not in normalize(f"{title} {author}"):
            continue
        epub = None
        web = None
        cover = None
        for link in entry.findall("a:link", ns):
            href = link.attrib.get("href", "")
            typ = link.attrib.get("type", "")
            rel = link.attrib.get("rel", "")
            full = urljoin("https://standardebooks.org", href)
            if "epub" in typ or full.endswith(".epub"):
                epub = full
            if typ == "text/html" or rel == "alternate":
                web = full
            if "image" in typ:
                cover = full
        results.append(BookResult(title=title, authors=author, source=SOURCE, epub_url=epub, web_url=web, cover_url=cover, summary=summary))
        if len(results) >= MAX_RESULTS_PER_SOURCE:
            break
    return results
