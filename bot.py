import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_author(book):
    return ", ".join(a.get("name", "") for a in book.get("authors", [])) or "Autor desconocido"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bot de libros legales.\n\n"
        "Comandos:\n"
        "/buscar dracula\n"
        "/gutenberg sherlock holmes\n"
        "/openlibrary harry potter\n"
        "/libro 1342"
    )

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Escribe así:\n/buscar dracula")
        return

    await update.message.reply_text("🔎 Buscando en bibliotecas legales...")

    mensajes = []

    # Project Gutenberg / Gutendex
    try:
        r = requests.get("https://gutendex.com/books/", params={"search": query}, timeout=20)
        results = r.json().get("results", [])[:5]

        if results:
            msg = "📘 Project Gutenberg:\n\n"
            for book in results:
                msg += (
                    f"📖 {book.get('title')}\n"
                    f"✍️ {get_author(book)}\n"
                    f"⬇️ /libro {book.get('id')}\n\n"
                )
            mensajes.append(msg)
    except Exception:
        pass

    # Open Library
    try:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params={"q": query, "limit": 5},
            timeout=20
        )
        docs = r.json().get("docs", [])[:5]

        if docs:
            msg = "🌐 Open Library:\n\n"
            for d in docs:
                title = d.get("title", "Sin título")
                authors = ", ".join(d.get("author_name", [])[:2]) or "Autor desconocido"
                year = d.get("first_publish_year", "s/f")
                key = d.get("key", "")
                link = f"https://openlibrary.org{key}"

                ebook_status = d.get("ebook_access", "unknown")
                msg += (
                    f"📖 {title}\n"
                    f"✍️ {authors}\n"
                    f"📅 {year}\n"
                    f"🔗 {link}\n"
                    f"Estado: {ebook_status}\n\n"
                )
            mensajes.append(msg)
    except Exception:
        pass

    if not mensajes:
        await update.message.reply_text("No encontré resultados legales.")
        return

    for msg in mensajes:
        await update.message.reply_text(msg[:4000])

async def gutenberg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.args = context.args
    await buscar(update, context)

async def openlibrary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Escribe así:\n/openlibrary don quijote")
        return

    r = requests.get(
        "https://openlibrary.org/search.json",
        params={"q": query, "limit": 10},
        timeout=20
    )
    docs = r.json().get("docs", [])

    if not docs:
        await update.message.reply_text("No encontré resultados en Open Library.")
        return

    msg = "🌐 Resultados en Open Library:\n\n"
    for d in docs[:8]:
        title = d.get("title", "Sin título")
        authors = ", ".join(d.get("author_name", [])[:2]) or "Autor desconocido"
        year = d.get("first_publish_year", "s/f")
        key = d.get("key", "")
        link = f"https://openlibrary.org{key}"
        access = d.get("ebook_access", "unknown")

        msg += (
            f"📖 {title}\n"
            f"✍️ {authors}\n"
            f"📅 {year}\n"
            f"🔗 {link}\n"
            f"Estado: {access}\n\n"
        )

    await update.message.reply_text(msg[:4000])

async def libro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Escribe así:\n/libro 1342")
        return

    book_id = context.args[0]

    r = requests.get(f"https://gutendex.com/books/{book_id}", timeout=20)

    if r.status_code != 200:
        await update.message.reply_text("No encontré ese libro en Project Gutenberg.")
        return

    book = r.json()
    title = book.get("title", "libro")
    formats = book.get("formats", {})

    epub_url = None
    for mime, link in formats.items():
        if "epub" in mime:
            epub_url = link
            break

    if not epub_url:
        await update.message.reply_text("Este libro no tiene ePub disponible.")
        return

    await update.message.reply_document(
        document=epub_url,
        filename=f"{title[:80]}.epub",
        caption=f"📖 {title}\nFuente: Project Gutenberg"
    )

def main():
    if not TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CommandHandler("gutenberg", buscar))
    app.add_handler(CommandHandler("openlibrary", openlibrary))
    app.add_handler(CommandHandler("libro", libro))

    app.run_polling()

if __name__ == "__main__":
    main()