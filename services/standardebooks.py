import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from models import BookResult
from utils import score_result
from .base import get_text

SOURCE = 'Standard Ebooks'

async def search(query: str, limit: int = 5):
    xml = await get_text('https://standardebooks.org/opds/all')
    root = ET.fromstring(xml)
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    q = query.lower()
    out = []
    for entry in root.findall('a:entry', ns):
        title = entry.findtext('a:title', default='', namespaces=ns)
        author = entry.findtext('a:author/a:name', default='', namespaces=ns)
        if q not in f'{title} {author}'.lower() and score_result(query, title, [author]) < 70:
            continue
        epub = web = cover = summary = None
        summary = entry.findtext('a:summary', default='', namespaces=ns)
        for link in entry.findall('a:link', ns):
            href = link.attrib.get('href','')
            typ = link.attrib.get('type','')
            rel = link.attrib.get('rel','')
            full = urljoin('https://standardebooks.org', href)
            if 'epub' in typ or full.endswith('.epub'):
                epub = full
            elif typ == 'text/html' or rel == 'alternate':
                web = full
            elif 'image' in typ:
                cover = full
        out.append(BookResult(title=title, authors=[author] if author else [], source=SOURCE,
                              epub_url=epub, web_url=web, cover_url=cover, summary=summary,
                              score=score_result(query, title, [author])))
        if len(out) >= limit:
            break
    return out
