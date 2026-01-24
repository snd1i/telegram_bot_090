import json
import os
import threading
import time

class UserStorage:
    def __init__(self):
        self.lock = threading.Lock()
        # Railway uyumlu dosya yolu
        self.data_file = 'users_data.json'
        self.data = self._load_data()
        print(f"📦 Storage başlatıldı: {self.get_total_users()} kullanıcı")
    
    def _load_data(self):
        """Verileri dosyadan yükle"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"📂 {len(data.get('users', []))} kullanıcı yüklendi")
                    return data
            else:
                print("📂 Yeni veritabanı oluşturuluyor...")
                return {'users': [], 'chats': {}, 'metadata': {'created_at': time.time()}}
        except Exception as e:
            print(f"❌ Veri yükleme hatası: {e}")
            return {'users': [], 'chats': {}, 'metadata': {'created_at': time.time()}}
    
    def _save_data(self):
        """Verileri dosyaya kaydet"""
        try:
            # Railway'da atomic write için geçici dosya kullan
            temp_file = f"{self.data_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # Eski dosyayı sil ve yeni dosyayı taşı
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            os.rename(temp_file, self.data_file)
            
            return True
        except Exception as e:
            print(f"❌ Veri kaydetme hatası: {e}")
            return False
    
    def add_user(self, user_id, chat_id, username=None, first_name=None, last_name=None):
        """Yeni kullanıcı ekle"""
        with self.lock:
            user_id_str = str(user_id)
            
            # Kullanıcıyı ekle (tekilleştirme)
            if user_id not in self.data['users']:
                self.data['users'].append(user_id)
            
            # Chat bilgisini ekle/güncelle
            self.data['chats'][user_id_str] = {
                'chat_id': chat_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'last_seen': time.time()
            }
            
            # Metadata güncelle
            self.data['metadata']['last_updated'] = time.time()
            self.data['metadata']['total_updates'] = self.data['metadata'].get('total_updates', 0) + 1
            
            # Hemen kaydet
            success = self._save_data()
            if success:
                print(f"✅ Kullanıcı kaydedildi: {user_id} (Toplam: {len(self.data['users'])})")
            return success
    
    def get_total_users(self):
        """Toplam kullanıcı sayısı"""
        return len(self.data['users'])
    
    def get_all_users(self):
        """Tüm kullanıcıları getir"""
        return self.data['users']
    
    def get_user_chats(self):
        """Tüm chat bilgilerini getir"""
        return self.data['chats']
    
    def get_chat_id(self, user_id):
        """Kullanıcının chat ID'sini getir"""
        user_data = self.data['chats'].get(str(user_id), {})
        return user_data.get('chat_id')
    
    def get_stats(self):
        """İstatistikleri getir"""
        return {
            'total_users': self.get_total_users(),
            'total_chats': len(self.data['chats']),
            'metadata': self.data['metadata']
        }

# Global storage instance
storage = UserStorage()
