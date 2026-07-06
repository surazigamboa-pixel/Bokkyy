from urllib.parse import quote
from models import BookResult
from utils import score_result
from .base import get_json

SOURCE = 'Internet Archive'

async def search(query: str, limit: int = 5):
    data = await get_json('https://archive.org/advancedsearch.php', {
        'q': f'title:({query}) AND mediatype:texts',
        'fl[]': ['identifier','title','creator','year'],
        'rows': limit,
        'output': 'json'
    })
    docs = data.get('response', {}).get('docs', [])
    out = []
    for d in docs[:limit]:
        ident = d.get('identifier')
        title = d.get('title') or query
        creator = d.get('creator')
        authors = creator if isinstance(creator, list) else ([creator] if creator else [])
        epub = None
        try:
            meta = await get_json(f'https://archive.org/metadata/{ident}')
            for f in meta.get('files', []):
                name = f.get('name','')
                if name.lower().endswith('.epub'):
                    epub = f'https://archive.org/download/{ident}/{quote(name)}'
                    break
        except Exception:
            pass
        out.append(BookResult(
            title=title, authors=authors, source=SOURCE, epub_url=epub,
            web_url=f'https://archive.org/details/{ident}',
            cover_url=f'https://archive.org/services/img/{ident}', year=str(d.get('year','')),
            identifier=ident, score=score_result(query, title, authors)
        ))
    return out
