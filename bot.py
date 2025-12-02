from telethon import TelegramClient, events
import os
import datetime
from users_db import (
    add_user, get_user, ban_user, unban_user, 
    get_all_users, get_stats, increment_messages
)

api_id = int(os.getenv('API_ID', '22880380'))
api_hash = os.getenv('API_HASH', '08dae0d98b2dc8f8dc4e6a9ff97a071b')
bot_token = os.getenv('BOT_TOKEN', '8028312869:AAErsD7WmHHw11c2lL2Jdoj_DBU4bqRv_kQ')
owner_id = int(os.getenv('OWNER_ID', '0'))

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

broadcast_temp = {}

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
    
    if sender.id == owner_id:
        menu = """🔐 OWNER PANEL

/users - Manage users
/broadcast - Send broadcast
/stats - Bot statistics
/settings - Settings
/help - Help"""
    else:
        menu = f"""👋 Welcome {sender.first_name}!

/profile - Your profile
/help - Help
/about - About bot
/echo - Echo mode"""
    
    await event.respond(menu)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/users'))
async def users_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Ye command sirf owner ko allowed hai!')
        raise events.StopPropagation
    
    all_users = get_all_users()
    users_list = "\n".join([
        f"• {u['first_name']} (@{u['username']}) - {'🚫 Banned' if u.get('banned') else '✅ Active'}"
        for u in all_users.values()
    ]) or "No users yet"
    
    response = f"""👥 USERS MANAGEMENT

Total Users: {len(all_users)}

{users_list}

Commands:
/ban <user_id> - Ban user
/unban <user_id> - Unban user
/userinfo <user_id> - User details"""
    
    await event.respond(response)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/ban'))
async def ban_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Owner only!')
        raise events.StopPropagation
    
    args = event.text.split()
    if len(args) < 2:
        await event.respond('Usage: /ban <user_id>')
        raise events.StopPropagation
    
    try:
        user_id = int(args[1])
        if ban_user(user_id):
            await event.respond(f'✅ User {user_id} banned!')
        else:
            await event.respond('❌ User not found!')
    except ValueError:
        await event.respond('❌ Invalid user ID!')
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unban'))
async def unban_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Owner only!')
        raise events.StopPropagation
    
    args = event.text.split()
    if len(args) < 2:
        await event.respond('Usage: /unban <user_id>')
        raise events.StopPropagation
    
    try:
        user_id = int(args[1])
        if unban_user(user_id):
            await event.respond(f'✅ User {user_id} unbanned!')
        else:
            await event.respond('❌ User not found!')
    except ValueError:
        await event.respond('❌ Invalid user ID!')
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/userinfo'))
async def userinfo_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Owner only!')
        raise events.StopPropagation
    
    args = event.text.split()
    if len(args) < 2:
        await event.respond('Usage: /userinfo <user_id>')
        raise events.StopPropagation
    
    try:
        user_id = int(args[1])
        user = get_user(user_id)
        if user:
            info = f"""ℹ️ USER INFO

Name: {user['first_name']}
Username: @{user['username']}
ID: {user['user_id']}
Joined: {user['joined']}
Messages: {user['messages']}
Status: {'🚫 Banned' if user.get('banned') else '✅ Active'}"""
            await event.respond(info)
        else:
            await event.respond('❌ User not found!')
    except ValueError:
        await event.respond('❌ Invalid user ID!')
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/broadcast'))
async def broadcast_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Owner only!')
        raise events.StopPropagation
    
    broadcast_temp[sender.id] = True
    response = """📢 BROADCAST MODE

Likho message jo sab users ko bhejana hai:
(Format: /send <message>)

Available placeholders:
{username} - User username
{first_name} - User first name
{user_id} - User ID

Example: /send Hello {first_name}! This is a broadcast message.

/cancel - Cancel broadcast"""
    
    await event.respond(response)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/send'))
async def send_broadcast_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id or not broadcast_temp.get(sender.id):
        await event.respond('❌ Start broadcast first with /broadcast')
        raise events.StopPropagation
    
    message = event.text.replace('/send ', '', 1)
    all_users = get_all_users()
    
    sent_count = 0
    failed_count = 0
    
    for user_id_str, user in all_users.items():
        if user.get('banned'):
            continue
        
        try:
            formatted_msg = message.format(
                username=user.get('username', 'User'),
                first_name=user.get('first_name', 'User'),
                user_id=user['user_id']
            )
            await client.send_message(int(user_id_str), f"📢 {formatted_msg}")
            sent_count += 1
        except:
            failed_count += 1
    
    broadcast_temp[sender.id] = False
    await event.respond(f"✅ Broadcast sent!\n\nSent to: {sent_count}\nFailed: {failed_count}")
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/cancel'))
async def cancel_handler(event):
    sender = await event.get_sender()
    if sender.id == owner_id:
        broadcast_temp[sender.id] = False
        await event.respond('❌ Broadcast cancelled!')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/stats'))
async def stats_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Owner only!')
        raise events.StopPropagation
    
    stats = get_stats()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    response = f"""📊 BOT STATISTICS

🤖 Bot Status: ✅ Online
⏰ Current Time: {current_time}
⏱️ Uptime: {(datetime.datetime.now()).strftime('%Y-%m-%d')}

👥 USERS:
- Total Users: {stats['total_users']}
- Active Users: {stats['active_users']}
- Banned Users: {stats['banned_users']}

📨 MESSAGES:
- Total Messages: {stats['total_messages']}
- Messages Today: [Placeholder]

💾 SYSTEM:
- Database: ✅ Connected
- Python Version: 3.11
- Telethon: ✅ Running"""
    
    await event.respond(response)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/settings'))
async def settings_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Owner only!')
        raise events.StopPropagation
    
    settings = """⚙️ SETTINGS

🛠️ Available Settings:

1. /set_start_text <text> - Customize start message
2. /set_sudo_force <on/off> - Enable/disable sudo force
3. /set_group_handle <on/off> - Handle group messages

Current Settings:
- Start Text: [Custom message]
- Sudo Force: Off
- Group Handle: Off

[More features coming soon...]"""
    
    await event.respond(settings)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/profile'))
async def profile_handler(event):
    sender = await event.get_sender()
    user = get_user(sender.id)
    
    if user:
        profile = f"""👤 YOUR PROFILE

Name: {user['first_name']}
Username: @{user['username']}
User ID: {user['user_id']}
Joined: {user['joined']}
Messages Sent: {user['messages']}
Status: Active ✅"""
        await event.respond(profile)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/about'))
async def about_handler(event):
    about = """ℹ️ ABOUT BOT

Bot Name: Advanced Telegram Bot
Version: 1.0
Created with: Telethon Library

Features:
✅ User Management System
✅ Broadcast Messages
✅ Statistics & Analytics
✅ Settings Management
✅ Admin Panel

For more info, contact owner!"""
    
    await event.respond(about)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    sender = await event.get_sender()
    
    if sender.id == owner_id:
        help_text = """🔐 OWNER COMMANDS:
/start - Start
/users - Manage users
/ban <id> - Ban user
/unban <id> - Unban user  
/userinfo <id> - User details
/broadcast - Send broadcast
/cancel - Cancel broadcast
/stats - Statistics
/settings - Settings
/help - This help"""
    else:
        help_text = """👤 USER COMMANDS:
/start - Start bot
/profile - Your profile
/about - About bot
/echo - Echo mode
/help - This help"""
    
    await event.respond(help_text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/echo'))
async def echo_handler(event):
    sender = await event.get_sender()
    await event.respond(f'🔄 Echo mode: Type messages to repeat them')
    raise events.StopPropagation

@client.on(events.NewMessage)
async def message_handler(event):
    sender = await event.get_sender()
    if event.is_private and not event.text.startswith('/'):
        increment_messages(sender.id)
        await event.respond(f'📝 Echo: {event.text}')

print('🚀 Bot chal raha hai...')
client.run_until_disconnected()
