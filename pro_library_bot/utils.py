import io
import re
import html
import httpx
from typing import Iterable, List
from models import BookResult
from config import USER_AGENT, REQUEST_TIMEOUT


def clean_filename(name: str) -> str:
    name = html.unescape(name or "libro")
    name = re.sub(r"[\\/:*?\"<>|]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:90] or "libro"


def normalize(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^\w\sáéíóúñü-]", " ", s, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip()


def dedupe(results: Iterable[BookResult]) -> List[BookResult]:
    seen = set()
    out = []
    for r in results:
        key = (normalize(r.title), normalize(r.authors), r.source, r.epub_url or r.web_url)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def rank_results(results: List[BookResult], query: str) -> List[BookResult]:
    q = normalize(query)
    for r in results:
        score = 0
        title = normalize(r.title)
        authors = normalize(r.authors)
        if q and q == title:
            score += 100
        if q and q in title:
            score += 60
        if q and q in authors:
            score += 35
        if r.epub_url:
            score += 50
        if r.cover_url:
            score += 5
        if r.summary:
            score += 5
        source_boost = {
            "Project Gutenberg": 30,
            "Standard Ebooks": 28,
            "Internet Archive": 18,
            "Open Library": 12,
            "Wikisource": 10,
            "ManyBooks": 8,
            "Feedbooks": 8,
        }
        score += source_boost.get(r.source, 0)
        r.score = score
    return sorted(results, key=lambda x: x.score, reverse=True)


async def download_bytes(url: str) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def make_file(data: bytes, filename: str) -> io.BytesIO:
    f = io.BytesIO(data)
    f.name = filename
    return f
