import json
import os
from datetime import datetime

USERS_FILE = 'users_data.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def add_user(user_id, username, first_name):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'joined': datetime.now().isoformat(),
            'messages': 0,
            'banned': False,
            'status': 'active'
        }
        save_users(users)
    return users[str(user_id)]

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))

def ban_user(user_id):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)]['banned'] = True
        save_users(users)
        return True
    return False

def unban_user(user_id):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)]['banned'] = False
        save_users(users)
        return True
    return False

def increment_messages(user_id):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)]['messages'] += 1
        save_users(users)

def get_all_users():
    return load_users()

def get_stats():
    users = load_users()
    total = len(users)
    banned = sum(1 for u in users.values() if u.get('banned', False))
    active = total - banned
    return {
        'total_users': total,
        'banned_users': banned,
        'active_users': active,
        'total_messages': sum(u.get('messages', 0) for u in users.values())
    }
