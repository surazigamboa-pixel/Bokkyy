from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class BookResult:
    title: str
    source: str
    authors: str = "Autor desconocido"
    epub_url: Optional[str] = None
    web_url: Optional[str] = None
    cover_url: Optional[str] = None
    summary: Optional[str] = None
    language: Optional[str] = None
    year: Optional[str] = None
    identifier: Optional[str] = None
    score: int = 0
    meta: Dict = field(default_factory=dict)

    @property
    def has_epub(self) -> bool:
        return bool(self.epub_url)
