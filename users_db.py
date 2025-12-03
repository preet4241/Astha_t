import sqlite3
import os
from datetime import datetime

DB_FILE = 'bot_database.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined TEXT,
            messages INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    """Add new user to database"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, joined)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"Error adding user: {e}")
    finally:
        conn.close()

def get_user(user_id):
    """Get user from database"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'user_id': user[0],
            'username': user[1],
            'first_name': user[2],
            'joined': user[3],
            'messages': user[4],
            'banned': user[5],
            'status': user[6]
        }
    return None

def ban_user(user_id):
    """Ban user"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET banned = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def unban_user(user_id):
    """Unban user"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET banned = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def increment_messages(user_id):
    """Increment message count"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET messages = messages + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    """Get all users"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    
    result = {}
    for user in users:
        result[str(user[0])] = {
            'user_id': user[0],
            'username': user[1],
            'first_name': user[2],
            'joined': user[3],
            'messages': user[4],
            'banned': user[5],
            'status': user[6]
        }
    return result

def get_stats():
    """Get bot statistics"""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE banned = 1')
    banned = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(messages) FROM users')
    total_messages = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_users': total,
        'banned_users': banned,
        'active_users': total - banned,
        'total_messages': total_messages
    }

def init_settings_table():
    """Initialize settings table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def set_setting(key, value):
    """Set a setting value"""
    init_settings_table()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_setting(key, default=''):
    """Get a setting value"""
    init_settings_table()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default
