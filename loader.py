# loader.py - Otomatik eklenti yükleyici
import os
import importlib
from telegram.ext import Application

def load_extensions(application):
    """extensions/ klasöründeki tüm dosyaları yükler"""
    extensions_dir = "extensions"
    
    if not os.path.exists(extensions_dir):
        print(f"📁 Creating {extensions_dir}/ directory...")
        os.makedirs(extensions_dir)
        # İlk eklenti dosyasını oluştur
        with open(f"{extensions_dir}/example.py", "w", encoding="utf-8") as f:
            f.write('''# example.py - Örnek eklenti
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def example_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Örnek komut"""
    await update.message.reply_text("👋 Merhaba! Bu bir örnek komut.")

# OTOMATİK YÜKLEME İÇİN BU FONKSİYON GEREKLİ
def setup(app: Application):
    """Komutları bot'a ekler"""
    app.add_handler(CommandHandler("example", example_command))
    print("✅ Example extension loaded!")
''')
        print("✅ Created example.py")
        return
    
    print(f"📂 Scanning {extensions_dir}/ directory...")
    
    loaded_count = 0
    for filename in os.listdir(extensions_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # .py'yi kaldır
            
            try:
                # Modülü import et
                module = importlib.import_module(f"extensions.{module_name}")
                
                # setup fonksiyonunu çağır
                if hasattr(module, 'setup'):
                    module.setup(application)
                    print(f"   ✅ {module_name}.py loaded")
                    loaded_count += 1
                else:
                    print(f"   ⚠️ {module_name}.py has no setup() function")
                    
            except Exception as e:
                print(f"   ❌ Error loading {filename}: {e}")
    
    print(f"📊 Total extensions loaded: {loaded_count}")
