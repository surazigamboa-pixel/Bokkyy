from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from models import BookResult


def result_keyboard(results: List[BookResult]) -> InlineKeyboardMarkup:
    rows = []
    epub_i = 0
    link_i = 0
    for i, r in enumerate(results[:10]):
        label = f"📥 {r.source}" if r.epub_url else f"🔗 {r.source}"
        data = f"epub:{i}" if r.epub_url else f"link:{i}"
        rows.append([InlineKeyboardButton(label, callback_data=data)])
    rows.append([InlineKeyboardButton("📋 Ver todos los enlaces", callback_data="links:all")])
    return InlineKeyboardMarkup(rows)
