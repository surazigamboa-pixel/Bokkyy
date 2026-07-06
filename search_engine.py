import asyncio
from config import MAX_RESULTS_PER_SOURCE
from utils import dedupe_results
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

async def search_all(query: str):
    tasks = [svc.search(query, MAX_RESULTS_PER_SOURCE) for svc in SERVICES]
    raw = await asyncio.gather(*tasks, return_exceptions=True)
    results = []
    errors = []
    for svc, item in zip(SERVICES, raw):
        if isinstance(item, Exception):
            errors.append(f'{svc.__name__}: {item}')
            continue
        results.extend(item)
    return dedupe_results(results), errors


def choose_best_epubs(results, count=2):
    return [r for r in results if r.epub_url][:count]


def format_links(results, max_items=10):
    lines = ['🔗 Fuentes legales encontradas:']
    shown = 0
    for r in results:
        if not r.web_url and not r.epub_url:
            continue
        icon = '📥' if r.epub_url else '🔎'
        url = r.web_url or r.epub_url
        lines.append(f"\n{icon} {r.title}\nFuente: {r.source}\nAutor: {r.author_text}\n{url}")
        shown += 1
        if shown >= max_items:
            break
    return '\n'.join(lines) if shown else 'No encontré enlaces legales útiles.'
