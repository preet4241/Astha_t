from telethon import TelegramClient, events, Button
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

def get_greeting():
    """Get greeting based on current time"""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
    
    greeting = get_greeting()
    stats = get_stats()
    
    if sender.id == owner_id:
        buttons = [
            [Button.inline('🛠️ Tools', b'owner_tools')],
            [Button.inline('👥 Users', b'owner_users'), Button.inline('📢 Broadcast', b'owner_broadcast')],
            [Button.inline('📊 Status', b'owner_status'), Button.inline('⚙️ Settings', b'owner_settings')],
        ]
        owner_text = f"""{greeting} Boss 👑

🤖 Status: 🟢 Active
👥 Users: {stats['total_users']} | ✅ Active: {stats['active_users']}

━━━━━━━━━━━━━━━━
Your Control Desk:

👥 Users - User management
📢 Broadcast - Send messages
📊 Status - View statistics
⚙️ Settings - Configure bot

━━━━━━━━━━━━━━━━"""
        await event.respond(owner_text, buttons=buttons)
    else:
        buttons = [
            [Button.inline('🛠️ Tools', b'user_tools')],
            [Button.inline('👤 Profile', b'user_profile'), Button.inline('❓ Help', b'user_help')],
            [Button.inline('ℹ️ About', b'user_about')],
        ]
        user_text = f"""{greeting} {sender.first_name}! 👋

🤖 Status: 🟢 Active
👥 Community: {stats['total_users']} Users

━━━━━━━━━━━━━━━━
What would you like to do?

👤 Profile - View your profile
❓ Help - Get help
ℹ️ About - About this bot

━━━━━━━━━━━━━━━━"""
        await event.respond(user_text, buttons=buttons)
    
    raise events.StopPropagation

@client.on(events.CallbackQuery)
async def callback_handler(event):
    sender = await event.get_sender()
    data = event.data
    
    is_owner = sender.id == owner_id
    
    if data == b'owner_tools':
        await event.edit('🛠️ Tools (coming soon...)', buttons=[[Button.inline('⬅️ Back', b'owner_back')]])
    
    elif data == b'owner_users':
        all_users = get_all_users()
        stats = get_stats()
        buttons = [
            [Button.inline('🚫 Ban', b'user_ban'), Button.inline('✅ Unban', b'user_unban')],
            [Button.inline('ℹ️ Info', b'user_info')],
            [Button.inline('⬅️ Back', b'owner_back')],
        ]
        users_text = f"""👥 USERS MANAGEMENT

━━━━━━━━━━━━━━━━
📊 Statistics:
  • Total Users: {stats['total_users']}
  • Active Users: {stats['active_users']}
  • Banned Users: {stats['banned_users']}
━━━━━━━━━━━━━━━━

👇 Choose an option below"""
        await event.edit(users_text, buttons=buttons)
    
    elif data == b'owner_broadcast':
        buttons = [
            [Button.inline('📝 Send Message', b'broadcast_send')],
            [Button.inline('⬅️ Back', b'owner_back')],
        ]
        broadcast_text = """📢 BROADCAST SYSTEM

━━━━━━━━━━━━━━━━
Send messages to all active users with custom placeholders:

👤 User Info:
• {first_name} - User's first name
• {username} - User's username  
• {user_id} - User's ID

📅 Date & Time:
• {date} - Current date (DD-MM-YYYY)
• {time} - Current time (HH:MM:SS)
• {datetime} - Full date & time

🔢 Stats:
• {total_users} - Total users
• {active_users} - Active users
• {banned_users} - Banned users

📝 Example:
"Hello {first_name}! Last update: {date} at {time}"
━━━━━━━━━━━━━━━━"""
        await event.edit(broadcast_text, buttons=buttons)
    
    elif data == b'broadcast_send':
        broadcast_temp[sender.id] = True
        buttons = [[Button.inline('❌ Cancel', b'owner_back')]]
        await event.edit('📝 Type your broadcast message:\n\n(Reply to this message with your content)', buttons=buttons)
    
    elif data == b'owner_status':
        stats = get_stats()
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        status_text = f"""📊 BOT STATUS

━━━━━━━━━━━━━━━━
🤖 System Status:
  ✅ Bot: Online
  ✅ Database: SQLite Connected
  
⏰ Time Information:
  📅 Date: {current_date}
  🕐 Time: {current_time}

━━━━━━━━━━━━━━━━
👥 User Statistics:
  • Total: {stats['total_users']}
  • Active: {stats['active_users']} ✅
  • Banned: {stats['banned_users']} 🚫

━━━━━━━━━━━━━━━━
📨 Message Stats:
  • Total Messages: {stats['total_messages']}
  • Today: [Tracking]

━━━━━━━━━━━━━━━━"""
        buttons = [[Button.inline('⬅️ Back', b'owner_back')]]
        await event.edit(status_text, buttons=buttons)
    
    elif data == b'owner_settings':
        buttons = [
            [Button.inline('✍️ Start Text', b'setting_start_text')],
            [Button.inline('🔄 Sudo Force', b'setting_sudo_force'), Button.inline('👥 Groups', b'setting_groups')],
            [Button.inline('⬅️ Back', b'owner_back')],
        ]
        settings_text = """⚙️ BOT SETTINGS

━━━━━━━━━━━━━━━━
Configure your bot behavior and features:

✍️ Start Text - Customize welcome message
🔄 Sudo Force - Enable/Disable admin features
👥 Groups - Handle group messages

━━━━━━━━━━━━━━━━"""
        await event.edit(settings_text, buttons=buttons)
    
    elif data == b'setting_start_text':
        await event.edit('✍️ Start Text: [Placeholder]\n\n(Coming soon...)', buttons=[[Button.inline('⬅️ Back', b'owner_settings')]])
    
    elif data == b'setting_sudo_force':
        await event.edit('🔄 Sudo Force: Off\n\n(Coming soon...)', buttons=[[Button.inline('⬅️ Back', b'owner_settings')]])
    
    elif data == b'setting_groups':
        await event.edit('👥 Group Handling: Off\n\n(Coming soon...)', buttons=[[Button.inline('⬅️ Back', b'owner_settings')]])
    
    elif data == b'user_tools':
        await event.edit('🛠️ Tools (coming soon...)', buttons=[[Button.inline('⬅️ Back', b'user_back')]])
    
    elif data == b'user_profile':
        user = get_user(sender.id)
        if user:
            profile_text = f"""👤 YOUR PROFILE

━━━━━━━━━━━━━━━━
📋 Profile Information:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • ID: {user['user_id']}

📊 Activity:
  • Messages Sent: {user['messages']}
  • Joined: {user['joined']}
  • Status: ✅ Active

━━━━━━━━━━━━━━━━"""
            await event.edit(profile_text, buttons=[[Button.inline('⬅️ Back', b'user_back')]])
    
    elif data == b'user_help':
        help_text = """❓ HELP

/hello - Greeting
/time - Current time
/profile - Your profile
/about - About bot"""
        await event.edit(help_text, buttons=[[Button.inline('⬅️ Back', b'user_back')]])
    
    elif data == b'user_about':
        about_text = """ℹ️ ABOUT BOT

Bot v1.0
Telethon Library
SQLite Database
Admin & User Management System"""
        await event.edit(about_text, buttons=[[Button.inline('⬅️ Back', b'user_back')]])
    
    elif data == b'user_ban':
        await event.edit('🚫 Ban User Feature\n\n(Coming soon...)', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
    
    elif data == b'user_unban':
        await event.edit('✅ Unban User Feature\n\n(Coming soon...)', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
    
    elif data == b'user_info':
        await event.edit('ℹ️ User Info\n\n(Coming soon...)', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
    
    elif data == b'owner_back':
        buttons = [
            [Button.inline('🛠️ Tools', b'owner_tools')],
            [Button.inline('👥 Users', b'owner_users'), Button.inline('📢 Broadcast', b'owner_broadcast')],
            [Button.inline('📊 Status', b'owner_status'), Button.inline('⚙️ Settings', b'owner_settings')],
        ]
        greeting = get_greeting()
        stats = get_stats()
        owner_text = f"""{greeting} Boss 👑

🤖 Status: 🟢 Active
👥 Users: {stats['total_users']} | ✅ Active: {stats['active_users']}

━━━━━━━━━━━━━━━━
Your Control Desk:

👥 Users - User management
📢 Broadcast - Send messages
📊 Status - View statistics
⚙️ Settings - Configure bot

━━━━━━━━━━━━━━━━"""
        await event.edit(owner_text, buttons=buttons)
    
    elif data == b'user_back':
        buttons = [
            [Button.inline('🛠️ Tools', b'user_tools')],
            [Button.inline('👤 Profile', b'user_profile'), Button.inline('❓ Help', b'user_help')],
            [Button.inline('ℹ️ About', b'user_about')],
        ]
        greeting = get_greeting()
        stats = get_stats()
        user_text = f"""{greeting}! 👋

🤖 Status: 🟢 Active
👥 Community: {stats['total_users']} Users

━━━━━━━━━━━━━━━━
What would you like to do?

👤 Profile - View your profile
❓ Help - Get help
ℹ️ About - About this bot

━━━━━━━━━━━━━━━━"""
        await event.edit(user_text, buttons=buttons)

@client.on(events.NewMessage(pattern='/hello'))
async def hello_handler(event):
    sender = await event.get_sender()
    await event.respond(f'👋 Hello {sender.first_name}!')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/time'))
async def time_handler(event):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    await event.respond(f'⏰ {current_time}')
    raise events.StopPropagation

@client.on(events.NewMessage)
async def message_handler(event):
    sender = await event.get_sender()
    
    if broadcast_temp.get(sender.id):
        message = event.text
        all_users = get_all_users()
        stats = get_stats()
        
        sent_count = 0
        failed_count = 0
        
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_datetime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        for user_id_str, user in all_users.items():
            if user.get('banned'):
                continue
            
            try:
                formatted_msg = message.format(
                    username=user.get('username', 'User'),
                    first_name=user.get('first_name', 'User'),
                    user_id=user['user_id'],
                    date=current_date,
                    time=current_time,
                    datetime=current_datetime,
                    total_users=stats['total_users'],
                    active_users=stats['active_users'],
                    banned_users=stats['banned_users']
                )
                await client.send_message(int(user_id_str), f"📢 {formatted_msg}")
                sent_count += 1
            except:
                failed_count += 1
        
        broadcast_temp[sender.id] = False
        await event.respond(f"✅ Broadcast sent!\n\nSent to: {sent_count}\nFailed: {failed_count}")
    
    elif event.is_private and not event.text.startswith('/'):
        increment_messages(sender.id)
        await event.respond(f'📝 {event.text}')

print('🚀 Bot chal raha hai...')
client.run_until_disconnected()
