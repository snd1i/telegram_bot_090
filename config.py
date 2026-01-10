import os
from dotenv import load_dotenv

# .env dosyasını yükle (yerel geliştirme için)
load_dotenv()

# Bot token'i (Railway'dan alınacak)
TOKEN = os.getenv("TOKEN", "")

# Kanal bilgileri
CHANNEL_USERNAME = "@KurdceBotlar"  # Kullanıcı adı
CHANNEL_LINK = "https://t.me/+wet-9MZuj044ZGQy"
CHANNEL_ID = -1002072605977  # Kanal ID'si

# Dosya yolları
DB_FILE = "users.json"

# Varsayılan dil (ISO kodları)
DEFAULT_LANGUAGE = "en"

# Bot bilgileri
BOT_NAME = "MultiLanguage Bot"
BOT_VERSION = "1.0"
