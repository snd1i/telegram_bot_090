import json
import os
from datetime import datetime

class Database:
    def __init__(self, db_file="users.json"):
        self.db_file = db_file
        self.users = self.load_data()
    
    def load_data(self):
        """Kullanıcı verilerini yükle"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Kullanıcı verilerini kaydet"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def get_user(self, user_id):
        """Kullanıcıyı getir"""
        return self.users.get(str(user_id))
    
    def create_user(self, user_id, username=None, first_name=None, last_name=None):
        """Yeni kullanıcı oluştur"""
        user_data = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "language": None,  # Henüz dil seçmedi
            "selected_language": False,  # Dil seçti mi?
            "subscribed": False,  # Kanala abone mi?
            "first_start": True,  # İlk defa mı /start yapıyor?
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        
        self.users[str(user_id)] = user_data
        self.save_data()
        return user_data
    
    def update_user(self, user_id, **kwargs):
        """Kullanıcıyı güncelle"""
        user_id = str(user_id)
        if user_id in self.users:
            self.users[user_id].update(kwargs)
            self.users[user_id]["last_seen"] = datetime.now().isoformat()
            self.save_data()
            return True
        return False
    
    def set_language(self, user_id, language_code):
        """Kullanıcının dilini ayarla"""
        return self.update_user(user_id, language=language_code, selected_language=True)
    
    def set_subscribed(self, user_id, subscribed=True):
        """Abonelik durumunu ayarla"""
        return self.update_user(user_id, subscribed=subscribed)
    
    def set_first_start(self, user_id, first_start=False):
        """İlk start durumunu ayarla"""
        return self.update_user(user_id, first_start=first_start)

# Global database instance
db = Database()
