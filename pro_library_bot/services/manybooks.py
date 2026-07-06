from urllib.parse import quote
from models import BookResult

SOURCE = "ManyBooks"

async def search(query: str):
    # ManyBooks does not provide a simple public API for direct EPUB downloads here.
    # We provide a legal search link only.
    return [BookResult(title=f"Buscar '{query}'", authors="ManyBooks", source=SOURCE, web_url=f"https://manybooks.net/search-book?field_keywords={quote(query)}")]
