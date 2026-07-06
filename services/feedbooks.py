from urllib.parse import quote
from models import BookResult

SOURCE = 'Feedbooks'

async def search(query: str, limit: int = 5):
    # Feedbooks ha cambiado su disponibilidad pública por región; se enlaza búsqueda legal.
    return [BookResult(
        title=f'Buscar “{query}” en Feedbooks', source=SOURCE,
        web_url=f'https://www.feedbooks.com/search?query={quote(query)}',
        score=50
    )]
