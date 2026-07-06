import os
import io
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote, urljoin
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

def clean_filename(name):
    return "".join(c for c in name[:80] if c.isalnum() or c in " _-").strip() or "libro"

async def send_epub(update, url, title, source):
    try:
        r = requests.get(url, timeout=40)
        r.raise_for_status()

        file = io.BytesIO(r.content)
        file.name = f"{clean_filename(title)}.epub"

        await update.message.reply_document(
            document=file,
            filename=file.name,
            caption=f"📖 {title}\nFuente: {source}"
        )
        return True
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Mándame el título de un libro.\n\n"
        "Buscaré ePub legales en bibliotecas abiertas.\n\n"
        "Ejemplo:\n"
        "dracula\n"
        "orgullo y prejuicio\n"
        "don quijote"
    )

async def buscar_libro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text("🔎 Buscando ePub legal...")

    # 1. Project Gutenberg
    try:
        r = requests.get(
            "https://gutendex.com/books/",
            params={"search": query},
            timeout=20
        )
        books = r.json().get("results", [])

        for book in books[:5]:
            title = book.get("title", query)
            formats = book.get("formats", {})

            epub_url = None
            for mime, link in formats.items():
                if "epub" in mime and "images" in mime:
                    epub_url = link
                    break

            if not epub_url:
                for mime, link in formats.items():
                    if "epub" in mime:
                        epub_url = link
                        break

            if epub_url:
                if await send_epub(update, epub_url, title, "Project Gutenberg"):
                    return

        if books:
            book_id = books[0].get("id")
            await update.message.reply_text(
                f"Encontré una opción en Project Gutenberg:\n"
                f"https://www.gutenberg.org/ebooks/{book_id}"
            )
            return
    except Exception:
        pass

    # 2. Standard Ebooks
    try:
        r = requests.get("https://standardebooks.org/opds/all", timeout=30)
        root = ET.fromstring(r.content)
        ns = {"a": "http://www.w3.org/2005/Atom"}

        q = query.lower()

        for entry in root.findall("a:entry", ns):
            title = entry.findtext("a:title", default="", namespaces=ns)
            author = entry.findtext("a:author/a:name", default="", namespaces=ns)

            if q not in f"{title} {author}".lower():
                continue

            epub_url = None
            web_url = None

            for link in entry.findall("a:link", ns):
                href = link.attrib.get("href", "")
                typ = link.attrib.get("type", "")

                if href:
                    href = urljoin("https://standardebooks.org", href)

                if "epub" in typ or href.endswith(".epub"):
                    epub_url = href

                if typ == "text/html":
                    web_url = href

            if epub_url:
                if await send_epub(update, epub_url, title, "Standard Ebooks"):
                    return

            if web_url:
                await update.message.reply_text(
                    f"Encontré una opción en Standard Ebooks:\n{web_url}"
                )
                return
    except Exception:
        pass

    # 3. Internet Archive
    try:
        r = requests.get(
            "https://archive.org/advancedsearch.php",
            params={
                "q": f'title:({query}) AND mediatype:texts',
                "fl[]": ["identifier", "title"],
                "rows": 5,
                "output": "json"
            },
            timeout=25
        )

        docs = r.json().get("response", {}).get("docs", [])

        for item in docs:
            identifier = item.get("identifier")
            title = item.get("title", query)

            meta = requests.get(
                f"https://archive.org/metadata/{identifier}",
                timeout=20
            ).json()

            files = meta.get("files", [])

            for f in files:
                name = f.get("name", "")
                if name.lower().endswith(".epub"):
                    epub_url = f"https://archive.org/download/{identifier}/{quote(name)}"
                    if await send_epub(update, epub_url, title, "Internet Archive"):
                        return

            await update.message.reply_text(
                f"Encontré una opción en Internet Archive:\n"
                f"https://archive.org/details/{identifier}"
            )
            return
    except Exception:
        pass

    # 4. Open Library
    try:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params={"q": query, "limit": 1},
            timeout=20
        )
        docs = r.json().get("docs", [])

        if docs:
            key = docs[0].get("key")
            title = docs[0].get("title", query)

            await update.message.reply_text(
                f"Encontré una opción en Open Library:\n"
                f"📖 {title}\n"
                f"https://openlibrary.org{key}"
            )
            return
    except Exception:
        pass

    # 5. Wikisource
    try:
        wiki_url = f"https://en.wikisource.org/wiki/Special:Search?search={quote(query)}"
        await update.message.reply_text(
            f"No encontré ePub directo, pero puedes revisar Wikisource:\n{wiki_url}"
        )
        return
    except Exception:
        pass

    # 6. ManyBooks y Feedbooks como enlaces de búsqueda legal
    manybooks = f"https://manybooks.net/search-book?field_keywords={quote(query)}"
    feedbooks = f"https://www.feedbooks.com/search?query={quote(query)}"

    await update.message.reply_text(
        "No encontré ePub directo.\n\n"
        "Puedes revisar estas fuentes legales:\n\n"
        f"ManyBooks:\n{manybooks}\n\n"
        f"Feedbooks:\n{feedbooks}"
    )

def main():
    if not TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buscar_libro))

    app.run_polling()

if __name__ == "__main__":
    main()