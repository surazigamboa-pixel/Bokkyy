import httpx
from urllib.parse import quote
from models import BookResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE, USER_AGENT

SOURCE = "Internet Archive"

async def search(query: str):
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = await client.get(
            "https://archive.org/advancedsearch.php",
            params={"q": f'title:({query}) AND mediatype:texts', "fl[]": ["identifier", "title", "creator", "year"], "rows": MAX_RESULTS_PER_SOURCE, "output": "json"},
        )
        resp.raise_for_status()
        docs = resp.json().get("response", {}).get("docs", [])
        results = []
        for d in docs:
            ident = d.get("identifier")
            title = d.get("title", query)
            meta_resp = await client.get(f"https://archive.org/metadata/{ident}")
            epub = None
            cover = f"https://archive.org/services/img/{ident}" if ident else None
            if meta_resp.status_code == 200:
                files = meta_resp.json().get("files", [])
                for f in files:
                    name = f.get("name", "")
                    if name.lower().endswith(".epub"):
                        epub = f"https://archive.org/download/{ident}/{quote(name)}"
                        break
            creator = d.get("creator")
            if isinstance(creator, list):
                creator = ", ".join(creator)
            results.append(BookResult(title=title, authors=creator or "Autor desconocido", source=SOURCE, epub_url=epub, web_url=f"https://archive.org/details/{ident}", cover_url=cover, year=str(d.get("year", "")) or None, identifier=ident))
    return results
