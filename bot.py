import os
import requests
import xml.etree.ElementTree as ET
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

def safe_name(text):
    return "".join(c for c in text[:80] if c.isalnum() or c in " _-").strip() or "libro"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Mándame el título de un libro.\n\n"
        "Buscaré ePub en:\n"
        "• Project Gutenberg\n"
        "• Standard Ebooks\n"
        "• Internet Archive\n\n"
        "Ejemplo:\n"
        "dracula"
    )

async def send_epub(update, url, title, source):
    try:
        await update.message.reply_document(
            document=url,
            filename=f"{safe_name(title)}.epub",
            caption=f"📖 {title}\nFuente: {source}"
        )
        return True
    except Exception:
        return False

async def buscar_titulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query:
        return

    await update.message.reply_text("🔎 Buscando ePub legal...")

    # 1. Project Gutenberg
    try:
        r = requests.get(
            "https://gutendex.com/books/",
            params={"search": query},
            timeout=20
        )
        results = r.json().get("results", [])

        for book in results[:5]:
            title = book.get("title", "libro")
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
                ok = await send_epub(update, epub_url, title, "Project Gutenberg")
                if ok:
                    return

        if results:
            book_id = results[0].get("id")
            title = results[0].get("title", query)
            await update.message.reply_text(
                f"📖 {title}\n"
                f"No pude enviar el ePub directo, pero está aquí:\n"
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

                if "epub" in typ or href.endswith(".epub"):
                    epub_url = href
                if typ == "text/html":
                    web_url = href

            if epub_url:
                ok = await send_epub(update, epub_url, title, "Standard Ebooks")
                if ok:
                    return

            if web_url:
                await update.message.reply_text(
                    f"📖 {title}\n"
                    f"No pude enviar el ePub directo, pero está aquí:\n{web_url}"
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

            epub_file = None
            for f in files:
                name = f.get("name", "")
                if name.lower().endswith(".epub"):
                    epub_file = name
                    break

            if epub_file:
                epub_url = f"https://archive.org/download/{identifier}/{epub_file}"
                ok = await send_epub(update, epub_url, title, "Internet Archive")
                if ok:
                    return

            await update.message.reply_text(
                f"📖 {title}\n"
                f"No encontré ePub directo, pero puedes revisarlo aquí:\n"
                f"https://archive.org/details/{identifier}"
            )
            return
    except Exception:
        pass

    await update.message.reply_text(
        "No encontré un ePub legal directo para ese título.\n"
        "Prueba con otro título o con el autor."
    )

def main():
    if not TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buscar_titulo))
    app.run_polling()

if __name__ == "__main__":
    main()