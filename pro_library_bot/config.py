import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
MAX_RESULTS_PER_SOURCE = int(os.getenv("MAX_RESULTS_PER_SOURCE", "5"))
MAX_EPUBS_TO_SEND = int(os.getenv("MAX_EPUBS_TO_SEND", "2"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "18"))
USER_AGENT = "TelegramLegalLibraryBot/1.0 (+legal open/public domain sources)"
