import json
import os
from datetime import datetime
from config import DB_FILE

class Database:
    def __init__(self):
        self.users = self.load_data()
    
    def load_data(self):
        """Kullanıcıları yükle"""
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Kullanıcıları kaydet"""
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False
    
    def get_user(self, user_id):
        """Kullanıcıyı getir"""
        return self.users.get(str(user_id))
    
    def create_user(self, user_id, username=None, first_name=None, language_code=None):
        """Yeni kullanıcı oluştur"""
        # Circular import'u önlemek için fonksiyonu buraya taşıdım
        def detect_language(language_code):
            if language_code:
                if language_code.startswith('tr'):
                    return "tr"
                elif language_code.startswith('ar'):
                    return "ar"
                elif language_code in ['ku', 'ckb']:
                    return "ckb"
                elif language_code.startswith('en'):
                    return "en"
            return "en"
        
        default_lang = detect_language(language_code)
        
        user_data = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "language": default_lang,
            "selected_language": False,
            "subscribed": False,
            "first_start": True,
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        
        self.users[str(user_id)] = user_data
        self.save_data()
        return user_data
    
    def update_user(self, user_id, **kwargs):
        """Kullanıcıyı güncelle"""
        user_id_str = str(user_id)
        if user_id_str in self.users:
            self.users[user_id_str].update(kwargs)
            self.users[user_id_str]["last_seen"] = datetime.now().isoformat()
            self.save_data()
            return True
        return False

# Global database instance
db = Database()
