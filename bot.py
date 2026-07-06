import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Hola, soy tu bot de libros legales en ePub.\n\n"
        "Usa:\n"
        "/buscar orgullo prejuicio\n"
        "/libro 1342"
    )

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Escribe algo así:\n/buscar dracula")
        return

    url = "https://gutendex.com/books/"
    r = requests.get(url, params={"search": query}, timeout=20)
    data = r.json()

    results = data.get("results", [])

    if not results:
        await update.message.reply_text("No encontré libros con esa búsqueda.")
        return

    mensaje = "📚 Resultados:\n\n"

    for book in results[:8]:
        title = book.get("title", "Sin título")
        authors = ", ".join(a["name"] for a in book.get("authors", [])) or "Autor desconocido"
        book_id = book.get("id")

        mensaje += f"📖 {title}\n✍️ {authors}\nID: {book_id}\nUsa: /libro {book_id}\n\n"

    await update.message.reply_text(mensaje[:4000])

async def libro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usa así:\n/libro 1342")
        return

    book_id = context.args[0]

    r = requests.get(f"https://gutendex.com/books/{book_id}", timeout=20)

    if r.status_code != 200:
        await update.message.reply_text("No encontré ese libro.")
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
    app.add_handler(CommandHandler("libro", libro))

    app.run_polling()

if __name__ == "__main__":
    main()