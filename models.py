from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BookResult:
    title: str
    source: str
    authors: list[str] = field(default_factory=list)
    epub_url: Optional[str] = None
    web_url: Optional[str] = None
    cover_url: Optional[str] = None
    summary: Optional[str] = None
    language: Optional[str] = None
    year: Optional[str] = None
    identifier: Optional[str] = None
    score: int = 0

    @property
    def author_text(self) -> str:
        return ', '.join([a for a in self.authors if a]) or 'Autor desconocido'

    @property
    def has_epub(self) -> bool:
        return bool(self.epub_url)
