import httpx
from models import BookResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE, USER_AGENT

SOURCE = "Project Gutenberg"

async def search(query: str):
    url = "https://gutendex.com/books/"
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url, params={"search": query})
        resp.raise_for_status()
        data = resp.json()
    results = []
    for b in data.get("results", [])[:MAX_RESULTS_PER_SOURCE]:
        formats = b.get("formats", {})
        epub = None
        cover = None
        for mime, link in formats.items():
            if "image/jpeg" in mime:
                cover = link
            if "epub" in mime and "images" in mime:
                epub = link
        if not epub:
            for mime, link in formats.items():
                if "epub" in mime:
                    epub = link
                    break
        book_id = b.get("id")
        authors = ", ".join(a.get("name", "") for a in b.get("authors", [])) or "Autor desconocido"
        results.append(BookResult(
            title=b.get("title", query),
            authors=authors,
            source=SOURCE,
            epub_url=epub,
            web_url=f"https://www.gutenberg.org/ebooks/{book_id}" if book_id else None,
            cover_url=cover,
            language=", ".join(b.get("languages", [])) or None,
            identifier=str(book_id) if book_id else None,
            meta={"downloads": b.get("download_count")}
        ))
    return results
