from models import BookResult
from utils import score_result
from .base import get_json

SOURCE = 'Open Library'

async def search(query: str, limit: int = 5):
    data = await get_json('https://openlibrary.org/search.json', {'q': query, 'limit': limit})
    results = []
    for d in data.get('docs', [])[:limit]:
        key = d.get('key') or ''
        cover = None
        if d.get('cover_i'):
            cover = f"https://covers.openlibrary.org/b/id/{d['cover_i']}-L.jpg"
        authors = d.get('author_name', [])[:3]
        title = d.get('title','Sin título')
        results.append(BookResult(
            title=title, authors=authors, source=SOURCE, epub_url=None,
            web_url=f'https://openlibrary.org{key}' if key else 'https://openlibrary.org',
            cover_url=cover, year=str(d.get('first_publish_year','')),
            language=','.join((d.get('language') or [])[:3]), identifier=key,
            score=score_result(query, title, authors)
        ))
    return results
