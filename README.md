# Telegram Legal Library Bot

Bot de Telegram para buscar libros en fuentes abiertas y legales.

## Fuentes incluidas

- Project Gutenberg
- Standard Ebooks
- Internet Archive
- Open Library
- Wikisource
- ManyBooks
- Feedbooks

## Funciones

- Búsqueda por título, autor o ISBN.
- Búsqueda simultánea en varias fuentes.
- Envía ePub legal directo cuando existe.
- Si no existe ePub directo, muestra enlaces legales.
- Botones para elegir ediciones.
- Historial por usuario.
- Favoritos por usuario.

## Variables de entorno

En Railway agrega:

```txt
TELEGRAM_BOT_TOKEN=tu_token_de_BotFather
```

Opcionales:

```txt
MAX_RESULTS_PER_SOURCE=5
SEND_TOP_EPUBS=2
REQUEST_TIMEOUT=25
```

## Deploy en Railway

1. Sube todos los archivos a la raíz del repositorio.
2. Railway detectará `Procfile` y ejecutará:

```txt
worker: python bot.py
```

3. Espera el deploy y prueba el bot con:

```txt
dracula
```

## Nota legal

Este bot está diseñado para usar fuentes de dominio público, contenido con licencia abierta o páginas legales de consulta/préstamo. No está diseñado para eludir pagos, DRM, restricciones de préstamo o derechos de autor.
