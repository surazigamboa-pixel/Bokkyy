import httpx
from config import REQUEST_TIMEOUT, USER_AGENT

async def get_json(url: str, params: dict | None = None):
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers={'User-Agent': USER_AGENT}, follow_redirects=True) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

async def get_text(url: str, params: dict | None = None):
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers={'User-Agent': USER_AGENT}, follow_redirects=True) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.text

async def get_bytes(url: str):
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers={'User-Agent': USER_AGENT}, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content, r.headers.get('content-type', '')
