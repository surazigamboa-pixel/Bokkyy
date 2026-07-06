import html
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import BOT_TOKEN, MAX_EPUBS_TO_SEND
from models import BookResult
from search_engine import search_all
from utils import clean_filename, download_bytes, make_file
from storage.store import add_history, get_history

RESULT_CACHE = {}


def format_result(r: BookResult, idx: int) -> str:
    marker = "📥 ePub" if r.epub_url else "🔗 Link"
    parts = [
        f"{idx}. <b>{html.escape(r.title)}</b>",
        f"✍️ {html.escape(r.authors or 'Autor desconocido')}",
        f"🏛️ {html.escape(r.source)} · {marker}",
    ]
    if r.year:
        parts.append(f"📅 {html.escape(str(r.year))}")
    if r.language:
        parts.append(f"🌍 {html.escape(str(r.language))}")
    return "\n".join(parts)


def build_keyboard(results: List[BookResult]) -> InlineKeyboardMarkup:
    rows = []
    for i, r in enumerate(results[:10]):
        if r.epub_url:
            rows.append([InlineKeyboardButton(f"📥 Descargar #{i+1} ({r.source})", callback_data=f"epub:{i}")])
        elif r.web_url:
            rows.append([InlineKeyboardButton(f"🔗 Abrir #{i+1} ({r.source})", url=r.web_url)])
    rows.append([InlineKeyboardButton("📋 Ver todos los links", callback_data="links:all")])
    rows.append([InlineKeyboardButton("🕘 Historial", callback_data="history:show")])
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 <b>Biblioteca ePub legal</b>\n\n"
        "Mándame un título, autor o ISBN. Buscaré en varias fuentes abiertas y legales.\n\n"
        "Si encuentro ePub autorizado, te lo envío directo. Si no existe ePub, te doy los enlaces legales disponibles.\n\n"
        "Ejemplos:\n"
        "• dracula\n"
        "• orgullo y prejuicio\n"
        "• mary shelley frankenstein",
        parse_mode="HTML"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos:\n"
        "/start — inicio\n"
        "/help — ayuda\n"
        "/historial — últimas búsquedas\n\n"
        "También puedes mandar solo el título del libro."
    )


async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = get_history(update.effective_user.id)
    if not items:
        await update.message.reply_text("Aún no tienes historial.")
        return
    await update.message.reply_text("🕘 Últimas búsquedas:\n" + "\n".join(f"• {x}" for x in items[:10]))


async def search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query:
        return

    add_history(update.effective_user.id, query)
    status = await update.message.reply_text("🔎 Buscando en Project Gutenberg, Standard Ebooks, Internet Archive, Open Library, Wikisource, ManyBooks y Feedbooks...")

    results = await search_all(query)
    RESULT_CACHE[update.effective_user.id] = results

    if not results:
        await status.edit_text("No encontré resultados legales para esa búsqueda.")
        return

    epub_count = sum(1 for r in results if r.epub_url)
    msg = [f"📚 <b>Resultados para:</b> {html.escape(query)}", f"📥 ePubs encontrados: {epub_count}", ""]
    for i, r in enumerate(results[:8], start=1):
        msg.append(format_result(r, i))
        msg.append("")

    await status.edit_text("\n".join(msg)[:3900], parse_mode="HTML", reply_markup=build_keyboard(results))

    # Auto-envía el mejor ePub, pero no más de MAX_EPUBS_TO_SEND.
    sent = 0
    for r in results:
        if not r.epub_url:
            continue
        if sent >= MAX_EPUBS_TO_SEND:
            break
        try:
            data = await download_bytes(r.epub_url)
            file = make_file(data, f"{clean_filename(r.title)}.epub")
            await update.message.reply_document(document=file, filename=file.name, caption=f"📖 {r.title}\nFuente: {r.source}")
            sent += 1
        except Exception:
            continue

    if sent == 0:
        links = [r for r in results if r.web_url]
        if links:
            await update.message.reply_text("No pude enviar ePub directo. Te dejé los enlaces legales en los botones del resultado.")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    results = RESULT_CACHE.get(user_id, [])

    if q.data.startswith("epub:"):
        idx = int(q.data.split(":", 1)[1])
        if idx >= len(results) or not results[idx].epub_url:
            await q.message.reply_text("Ese ePub ya no está disponible en caché. Busca el libro de nuevo.")
            return
        r = results[idx]
        try:
            data = await download_bytes(r.epub_url)
            file = make_file(data, f"{clean_filename(r.title)}.epub")
            await q.message.reply_document(document=file, filename=file.name, caption=f"📖 {r.title}\nFuente: {r.source}")
        except Exception:
            fallback = r.web_url or r.epub_url
            await q.message.reply_text(f"No pude enviar el ePub directo. Link legal:\n{fallback}")
        return

    if q.data == "links:all":
        if not results:
            await q.message.reply_text("Busca un libro primero.")
            return
        lines = ["🔗 Enlaces legales encontrados:\n"]
        for i, r in enumerate(results[:12], start=1):
            url = r.web_url or r.epub_url
            if url:
                lines.append(f"{i}. {r.title} — {r.source}\n{url}\n")
        await q.message.reply_text("\n".join(lines)[:4000])
        return

    if q.data == "history:show":
        items = get_history(user_id)
        await q.message.reply_text("🕘 Historial:\n" + "\n".join(f"• {x}" for x in items[:10]) if items else "Aún no tienes historial.")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("historial", historial))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_message))
    app.run_polling()


if __name__ == "__main__":
    main()
