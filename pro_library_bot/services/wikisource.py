import httpx
from urllib.parse import quote
from models import BookResult
from config import REQUEST_TIMEOUT, MAX_RESULTS_PER_SOURCE, USER_AGENT

SOURCE = "Wikisource"

async def search(query: str):
    headers = {"User-Agent": USER_AGENT}
    api = "https://en.wikisource.org/w/api.php"
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = await client.get(api, params={"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": MAX_RESULTS_PER_SOURCE})
        resp.raise_for_status()
        items = resp.json().get("query", {}).get("search", [])
    return [BookResult(title=i.get("title", query), authors="Wikisource", source=SOURCE, web_url=f"https://en.wikisource.org/wiki/{quote(i.get('title', '').replace(' ', '_'))}", summary=i.get("snippet")) for i in items]
