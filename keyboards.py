from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def result_keyboard(results):
    buttons = []
    for i, r in enumerate(results[:8]):
        label = f"{'📥' if r.epub_url else '🔗'} {r.source}: {r.title[:35]}"
        buttons.append([InlineKeyboardButton(label, callback_data=f'result:{i}')])
    buttons.append([InlineKeyboardButton('⭐ Ver favoritos', callback_data='favorites')])
    return InlineKeyboardMarkup(buttons)
