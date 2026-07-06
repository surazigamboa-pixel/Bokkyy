from urllib.parse import quote
from models import BookResult

SOURCE = "Feedbooks"

async def search(query: str):
    # Feedbooks public-domain catalog access varies by region/site availability; provide legal search link.
    return [BookResult(title=f"Buscar '{query}'", authors="Feedbooks", source=SOURCE, web_url=f"https://www.feedbooks.com/search?query={quote(query)}")]
