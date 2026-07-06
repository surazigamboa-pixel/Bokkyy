# Bot Telegram libros ePub legales

Bot modular para buscar libros en fuentes abiertas y legales. Si encuentra ePub autorizado, lo envía directo por Telegram; si no, muestra enlaces legales.

## Fuentes

- Project Gutenberg
- Standard Ebooks
- Internet Archive
- Open Library
- Wikisource
- ManyBooks
- Feedbooks

## Variables en Railway

Configura:

```text
TELEGRAM_BOT_TOKEN=tu_token_de_BotFather
```

## Deploy en Railway

El proyecto incluye:

- `Procfile`: `worker: python bot.py`
- `requirements.txt`
- `runtime.txt`

## Uso

En Telegram, manda solo el título:

```text
dracula
orgullo y prejuicio
mary shelley frankenstein
```

El bot responde con resultados, botones de descarga y enlaces legales.
