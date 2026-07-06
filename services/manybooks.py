from urllib.parse import quote
from models import BookResult
from utils import score_result

SOURCE = 'ManyBooks'

async def search(query: str, limit: int = 5):
    # ManyBooks no ofrece una API pública estable para descarga directa.
    # Se entrega enlace de búsqueda legal para contenido gratuito/dominio público.
    return [BookResult(
        title=f'Buscar “{query}” en ManyBooks', source=SOURCE,
        web_url=f'https://manybooks.net/search-book?field_keywords={quote(query)}',
        score=50
    )]
