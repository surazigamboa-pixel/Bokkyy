import httpx
from models import BookResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE, USER_AGENT

SOURCE = "Open Library"

async def search(query: str):
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = await client.get("https://openlibrary.org/search.json", params={"q": query, "limit": MAX_RESULTS_PER_SOURCE})
        resp.raise_for_status()
        docs = resp.json().get("docs", [])
    results = []
    for d in docs:
        key = d.get("key")
        cover = None
        if d.get("cover_i"):
            cover = f"https://covers.openlibrary.org/b/id/{d['cover_i']}-L.jpg"
        authors = ", ".join(d.get("author_name", [])[:3]) or "Autor desconocido"
        access = d.get("ebook_access")
        # Open Library usually requires legal borrow/read flow; use link, not forced download.
        results.append(BookResult(
            title=d.get("title", query), authors=authors, source=SOURCE, epub_url=None,
            web_url=f"https://openlibrary.org{key}" if key else None,
            cover_url=cover, year=str(d.get("first_publish_year", "")) or None,
            language=", ".join(d.get("language", [])[:3]) or None,
            meta={"access": access}
        ))
    return results
