import sqlite3
import json
import time
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_file="bot_database.db"):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'tr',
                is_banned INTEGER DEFAULT 0,
                is_subscribed INTEGER DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # İstatistikler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                date TEXT PRIMARY KEY,
                new_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name, last_name=""):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, join_date, last_active)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            ''', (user_id, username, first_name, last_name))
            
            # İstatistik güncelle
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute('''
                INSERT OR IGNORE INTO stats (date, new_users) VALUES (?, 0)
            ''', (today,))
            cursor.execute('''
                UPDATE stats SET new_users = new_users + 1 WHERE date = ?
            ''', (today,))
            
            self.conn.commit()
            return True
        except:
            return False
    
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()
    
    def update_user_language(self, user_id, language):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
        self.conn.commit()
    
    def update_subscription(self, user_id, is_subscribed):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_subscribed = ? WHERE user_id = ?', (is_subscribed, user_id))
        self.conn.commit()
    
    def ban_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()
    
    def unban_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
        self.conn.commit()
    
    def get_banned_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, username, first_name FROM users WHERE is_banned = 1')
        return cursor.fetchall()
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, username, first_name, language, join_date FROM users')
        return cursor.fetchall()
    
    def get_user_count(self, period="all"):
        cursor = self.conn.cursor()
        
        if period == "daily":
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            cursor.execute('SELECT COUNT(*) FROM users WHERE date(join_date) = date(?)', (date,))
        elif period == "weekly":
            date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            cursor.execute('SELECT COUNT(*) FROM users WHERE date(join_date) >= date(?)', (date,))
        elif period == "monthly":
            date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            cursor.execute('SELECT COUNT(*) FROM users WHERE date(join_date) >= date(?)', (date,))
        else:  # all
            cursor.execute('SELECT COUNT(*) FROM users')
        
        return cursor.fetchone()[0]
    
    def update_last_active(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET last_active = datetime("now") WHERE user_id = ?', (user_id,))
        self.conn.commit()

# Banned users için JSON (hızlı erişim)
class BannedUsers:
    def __init__(self, file="banned_users.json"):
        self.file = file
    
    def load(self):
        try:
            with open(self.file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save(self, data):
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add(self, user_id):
        data = self.load()
        if user_id not in data:
            data.append(user_id)
            self.save(data)
    
    def remove(self, user_id):
        data = self.load()
        if user_id in data:
            data.remove(user_id)
            self.save(data)
    
    def is_banned(self, user_id):
        data = self.load()
        return user_id in data
