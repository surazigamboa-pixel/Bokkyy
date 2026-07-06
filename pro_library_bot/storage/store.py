import json
import os
from typing import Dict, List

PATH = os.path.join(os.path.dirname(__file__), "data.json")

def _load() -> Dict:
    if not os.path.exists(PATH):
        return {"history": {}, "favorites": {}}
    try:
        with open(PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"history": {}, "favorites": {}}

def _save(data: Dict) -> None:
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_history(user_id: int, query: str) -> None:
    data = _load()
    key = str(user_id)
    data.setdefault("history", {}).setdefault(key, [])
    data["history"][key].insert(0, query)
    data["history"][key] = data["history"][key][:20]
    _save(data)

def get_history(user_id: int) -> List[str]:
    return _load().get("history", {}).get(str(user_id), [])
