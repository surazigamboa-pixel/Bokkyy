import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN')
MAX_RESULTS_PER_SOURCE = int(os.getenv('MAX_RESULTS_PER_SOURCE', '5'))
SEND_TOP_EPUBS = int(os.getenv('SEND_TOP_EPUBS', '2'))
REQUEST_TIMEOUT = float(os.getenv('REQUEST_TIMEOUT', '25'))
USER_AGENT = 'LegalTelegramLibraryBot/1.0 (open-source educational bot)'
