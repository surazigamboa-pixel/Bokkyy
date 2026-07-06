import asyncio
from typing import List
from models import BookResult
from utils import dedupe, rank_results
from services import gutenberg, standardebooks, internetarchive, openlibrary, wikisource, manybooks, feedbooks

SERVICES = [
    gutenberg,
    standardebooks,
    internetarchive,
    openlibrary,
    wikisource,
    manybooks,
    feedbooks,
]

async def _safe_search(service, query: str) -> List[BookResult]:
    try:
        return await service.search(query)
    except Exception as exc:
        return [BookResult(title=f"Error buscando en {getattr(service, 'SOURCE', service.__name__)}", source=getattr(service, 'SOURCE', service.__name__), summary=str(exc))]

async def search_all(query: str) -> List[BookResult]:
    tasks = [_safe_search(s, query) for s in SERVICES]
    groups = await asyncio.gather(*tasks)
    results = [r for g in groups for r in g if r and not r.title.lower().startswith("error buscando")]
    return rank_results(dedupe(results), query)
