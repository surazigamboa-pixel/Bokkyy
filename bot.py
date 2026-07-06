import html
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from config import TELEGRAM_TOKEN, SEND_TOP_EPUBS
from search_engine import search_all, choose_best_epubs, format_links
from services.base import get_bytes
from utils import clean_filename, bytes_file, add_history, get_history, add_favorite, get_favorites
from keyboards import result_keyboard

LAST_RESULTS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '📚 Hola. Mándame el título, autor o ISBN de un libro.\n\n'
        'Buscaré en bibliotecas abiertas y legales:\n'
        '• Project Gutenberg\n• Standard Ebooks\n• Internet Archive\n• Open Library\n• Wikisource\n• ManyBooks\n• Feedbooks\n\n'
        'Si encuentro ePub legal, lo envío. Si no, te doy enlaces legales.'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Comandos:\n'
        '/start — inicio\n'
        '/historial — últimas búsquedas\n'
        '/favoritos — favoritos guardados\n\n'
        'También puedes escribir solo el título: dracula, don quijote, pride and prejudice.'
    )

async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = get_history(update.effective_user.id)
    if not items:
        await update.message.reply_text('Aún no tienes historial.')
        return
    await update.message.reply_text('🕘 Historial:\n' + '\n'.join(f'• {x}' for x in items[:10]))

async def favorites_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    favs = get_favorites(update.effective_user.id)
    if not favs:
        await update.message.reply_text('Aún no tienes favoritos.')
        return
    lines = ['⭐ Favoritos:']
    for f in favs[:10]:
        lines.append(f"\n📖 {f.get('title')}\nFuente: {f.get('source')}\n{f.get('web_url') or f.get('epub_url') or ''}")
    await update.message.reply_text('\n'.join(lines)[:4000])

async def send_result(update, result):
    if result.epub_url:
        try:
            content, content_type = await get_bytes(result.epub_url)
            if len(content) > 49 * 1024 * 1024:
                raise RuntimeError('Archivo muy grande para Telegram')
            f = bytes_file(content, f'{clean_filename(result.title)}.epub')
            await update.message.reply_document(
                document=f,
                filename=f.name,
                caption=f'📖 {result.title}\n✍️ {result.author_text}\nFuente: {result.source}'
            )
            return True
        except Exception:
            pass
    if result.web_url:
        await update.message.reply_text(
            f'📖 {result.title}\n✍️ {result.author_text}\nFuente: {result.source}\n{result.web_url}'
        )
        return True
    return False

async def search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query:
        return
    user_id = update.effective_user.id
    add_history(user_id, query)
    status = await update.message.reply_text('🔎 Buscando en todas las fuentes abiertas...')
    results, errors = await search_all(query)
    LAST_RESULTS[user_id] = results
    if not results:
        await status.edit_text('No encontré resultados legales para esa búsqueda.')
        return

    epubs = choose_best_epubs(results, SEND_TOP_EPUBS)
    sent = 0
    for r in epubs:
        if await send_result(update, r):
            sent += 1

    links = format_links(results, max_items=10)
    intro = '✅ Encontré resultados.'
    if sent:
        intro += f' Envié {sent} ePub legal.'
    else:
        intro += ' No pude enviar ePub directo; te dejo enlaces legales.'
    await status.edit_text(intro)
    await update.message.reply_text(links[:4000], reply_markup=result_keyboard(results))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = update.effective_user.id
    data = q.data or ''
    if data == 'favorites':
        favs = get_favorites(user_id)
        if not favs:
            await q.message.reply_text('Aún no tienes favoritos.')
            return
        await q.message.reply_text('\n'.join(f"⭐ {f.get('title')} — {f.get('source')}" for f in favs[:10]))
        return
    if data.startswith('result:'):
        try:
            idx = int(data.split(':',1)[1])
            result = LAST_RESULTS.get(user_id, [])[idx]
        except Exception:
            await q.message.reply_text('Ese resultado ya no está disponible. Haz la búsqueda otra vez.')
            return
        await send_result(q, result)
        add_favorite(user_id, result.__dict__)
        await q.message.reply_text('⭐ Guardado en favoritos.')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print('ERROR:', context.error)


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError('Falta TELEGRAM_BOT_TOKEN')
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('historial', history_cmd))
    app.add_handler(CommandHandler('favoritos', favorites_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_message))
    app.add_error_handler(error_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
