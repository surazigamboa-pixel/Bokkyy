from urllib.parse import quote
from bs4 import BeautifulSoup
from models import BookResult
from utils import score_result
from .base import get_json, get_text

SOURCE = 'Wikisource'

async def search(query: str, limit: int = 5):
    data = await get_json('https://en.wikisource.org/w/api.php', {
        'action': 'query', 'list': 'search', 'srsearch': query,
        'format': 'json', 'srlimit': limit
    })
    out = []
    for s in data.get('query', {}).get('search', [])[:limit]:
        title = s.get('title','')
        snippet = BeautifulSoup(s.get('snippet',''), 'html.parser').get_text(' ')
        web = f'https://en.wikisource.org/wiki/{quote(title.replace(" ", "_"))}'
        out.append(BookResult(title=title, authors=[], source=SOURCE, web_url=web,
                              summary=snippet, score=score_result(query, title, [])))
    return out
