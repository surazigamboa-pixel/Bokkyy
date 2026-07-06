import io
import json
import os
import re
from pathlib import Path
from typing import Any
from rapidfuzz import fuzz

DATA_DIR = Path('storage')
DATA_DIR.mkdir(exist_ok=True)


def clean_filename(name: str) -> str:
    safe = ''.join(c for c in name[:90] if c.isalnum() or c in ' _-').strip()
    return safe or 'libro'


def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def score_result(query: str, title: str, authors: list[str] | None = None) -> int:
    haystack = f"{title} {' '.join(authors or [])}"
    return max(
        fuzz.token_set_ratio(normalize(query), normalize(title)),
        fuzz.token_set_ratio(normalize(query), normalize(haystack)),
    )


def dedupe_results(results):
    seen = set()
    out = []
    for r in sorted(results, key=lambda x: (x.has_epub, x.score), reverse=True):
        key = (normalize(r.title), normalize(r.author_text), r.source)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        pass
    return default


def save_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def memory_file(user_id: int) -> Path:
    return DATA_DIR / f'user_{user_id}.json'


def add_history(user_id: int, query: str):
    path = memory_file(user_id)
    data = load_json(path, {'history': [], 'favorites': []})
    data['history'] = [query] + [q for q in data.get('history', []) if q != query]
    data['history'] = data['history'][:20]
    save_json(path, data)


def get_history(user_id: int):
    return load_json(memory_file(user_id), {'history': [], 'favorites': []}).get('history', [])


def add_favorite(user_id: int, item: dict):
    path = memory_file(user_id)
    data = load_json(path, {'history': [], 'favorites': []})
    favs = data.get('favorites', [])
    key = item.get('web_url') or item.get('epub_url') or item.get('title')
    favs = [f for f in favs if (f.get('web_url') or f.get('epub_url') or f.get('title')) != key]
    favs.insert(0, item)
    data['favorites'] = favs[:50]
    save_json(path, data)


def get_favorites(user_id: int):
    return load_json(memory_file(user_id), {'history': [], 'favorites': []}).get('favorites', [])


def bytes_file(content: bytes, filename: str):
    bio = io.BytesIO(content)
    bio.name = filename
    bio.seek(0)
    return bio
