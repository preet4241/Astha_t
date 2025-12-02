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

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
    
    if sender.id == owner_id:
        buttons = [
            [Button.inline('🛠️ Tools', b'owner_tools')],
            [Button.inline('👥 Users', b'owner_users'), Button.inline('📢 Broadcast', b'owner_broadcast')],
            [Button.inline('📊 Status', b'owner_status'), Button.inline('⚙️ Settings', b'owner_settings')],
        ]
        await event.respond('🔐 OWNER PANEL', buttons=buttons)
    else:
        buttons = [
            [Button.inline('🛠️ Tools', b'user_tools')],
            [Button.inline('👤 Profile', b'user_profile'), Button.inline('❓ Help', b'user_help')],
            [Button.inline('ℹ️ About', b'user_about')],
        ]
        await event.respond(f'👋 Welcome {sender.first_name}!', buttons=buttons)
    
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

• {first_name} - User's first name
• {username} - User's username  
• {user_id} - User's ID

Example:
"Hello {first_name}! Welcome to our bot"
━━━━━━━━━━━━━━━━"""
        await event.edit(broadcast_text, buttons=buttons)
    
    elif data == b'broadcast_send':
        broadcast_temp[sender.id] = True
        buttons = [[Button.inline('❌ Cancel', b'owner_back')]]
        await event.edit('📝 Send your broadcast message:\n\nReply to this message', buttons=buttons)
    
    elif data == b'owner_status':
        stats = get_stats()
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        status_text = f"""📊 BOT STATUS

━━━━━━━━━━━━━━━━
🤖 System Status:
  ✅ Bot: Online
  ✅ Database: Connected
  
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
        owner_text = """🔐 OWNER PANEL

━━━━━━━━━━━━━━━━
Welcome to the owner control panel!

Manage your bot:
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
        user_text = """👋 USER MENU

━━━━━━━━━━━━━━━━
Explore features:

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
    if event.is_private and not event.text.startswith('/'):
        increment_messages(sender.id)
        await event.respond(f'📝 {event.text}')

print('🚀 Bot chal raha hai...')
client.run_until_disconnected()
