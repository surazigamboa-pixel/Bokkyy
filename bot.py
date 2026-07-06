import os
import requests
import xml.etree.ElementTree as ET
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bot de ePub.\n\n"
        "Usa:\n"
        "/buscar dracula\n"
        "/libro 1342\n\n"
        "Busca en Project Gutenberg y Standard Ebooks."
    )

def text_match(query, *texts):
    q = query.lower()
    return q in " ".join(t or "" for t in texts).lower()

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Escribe así:\n/buscar dracula")
        return

    await update.message.reply_text("🔎 Buscando ePub legales...")

    msg = "📚 Resultados:\n\n"

    # Project Gutenberg / Gutendex
    try:
        r = requests.get("https://gutendex.com/books/", params={"search": query}, timeout=20)
        for book in r.json().get("results", [])[:6]:
            title = book.get("title", "Sin título")
            authors = ", ".join(a.get("name", "") for a in book.get("authors", [])) or "Autor desconocido"
            book_id = book.get("id")
            msg += f"📘 {title}\n✍️ {authors}\n⬇️ /libro {book_id}\n\n"
    except Exception:
        pass

    # Standard Ebooks OPDS
    try:
        r = requests.get("https://standardebooks.org/opds/all", timeout=30)
        root = ET.fromstring(r.content)
        ns = {"a": "http://www.w3.org/2005/Atom"}

        found = 0
        for entry in root.findall("a:entry", ns):
            title = entry.findtext("a:title", default="", namespaces=ns)
            author_el = entry.find("a:author/a:name", ns)
            author = author_el.text if author_el is not None else "Autor desconocido"

            if not text_match(query, title, author):
                continue

            epub = None
            for link in entry.findall("a:link", ns):
                href = link.attrib.get("href", "")
                typ = link.attrib.get("type", "")
                if "epub" in typ or href.endswith(".epub"):
                    epub = href
                    break

            if epub:
                found += 1
                msg += f"📗 {title}\n✍️ {author}\n⬇️ /se {epub}\n\n"

            if found >= 6:
                break
    except Exception:
        pass

    if msg.strip() == "📚 Resultados:":
        await update.message.reply_text("No encontré ePub legales para esa búsqueda.")
    else:
        await update.message.reply_text(msg[:4000])

async def libro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Escribe así:\n/libro 1342")
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

async def se(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Falta el enlace de Standard Ebooks.")
        return

    epub_url = context.args[0]
    title = epub_url.rstrip("/").split("/")[-1].replace(".epub", "")

    await update.message.reply_document(
        document=epub_url,
        filename=f"{title[:80]}.epub",
        caption="📗 Fuente: Standard Ebooks"
    )

def main():
    if not TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CommandHandler("libro", libro))
    app.add_handler(CommandHandler("se", se))
    app.run_polling()

if __name__ == "__main__":
    main()