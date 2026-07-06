from models import BookResult
from utils import score_result
from .base import get_json

SOURCE = 'Project Gutenberg'

async def search(query: str, limit: int = 5):
    data = await get_json('https://gutendex.com/books/', {'search': query})
    results = []
    for b in data.get('results', [])[:limit]:
        formats = b.get('formats', {}) or {}
        epub = None
        for mime, link in formats.items():
            if 'epub' in mime and 'images' in mime:
                epub = link; break
        if not epub:
            for mime, link in formats.items():
                if 'epub' in mime:
                    epub = link; break
        authors = [a.get('name','') for a in b.get('authors', [])]
        bid = str(b.get('id'))
        results.append(BookResult(
            title=b.get('title','Sin título'), authors=authors, source=SOURCE,
            epub_url=epub, web_url=f'https://www.gutenberg.org/ebooks/{bid}',
            cover_url=formats.get('image/jpeg'), language=','.join(b.get('languages', []) or []),
            identifier=bid, score=score_result(query, b.get('title',''), authors)
        ))
    return results
