from telethon import TelegramClient, events
import os
from keyboards import (
    get_owner_main_keyboard, get_user_main_keyboard, get_users_detail_keyboard,
    get_settings_keyboard, get_back_keyboard
)

api_id = int(os.getenv('API_ID', '22880380'))
api_hash = os.getenv('API_HASH', '08dae0d98b2dc8f8dc4e6a9ff97a071b')
bot_token = os.getenv('BOT_TOKEN', '8028312869:AAErsD7WmHHw11c2lL2Jdoj_DBU4bqRv_kQ')
owner_id = int(os.getenv('OWNER_ID', '0'))

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    
    if sender.id == owner_id:
        await event.respond(
            '🔐 OWNER PANEL\n\nKya karna hai?',
            buttons=get_owner_main_keyboard()
        )
    else:
        await event.respond(
            f'👋 Welcome {sender.first_name}!\n\nKya karna hai?',
            buttons=get_user_main_keyboard()
        )
    
    raise events.StopPropagation

@client.on(events.CallbackQuery)
async def callback_handler(event):
    sender = await event.get_sender()
    callback_data = event.data
    
    sender_obj = await event.get_sender()
    is_owner = sender_obj.id == owner_id
    
    if callback_data == b'owner_tools':
        await event.edit('🛠️ Tools (coming soon...)', buttons=get_back_keyboard())
    
    elif callback_data == b'owner_users':
        users_text = """👥 USERS MANAGEMENT

📊 Total Users: 100
🚫 Banned Users: 5
✅ Active Users: 95

Kaunsa user manage karna hai?"""
        await event.edit(users_text, buttons=get_users_detail_keyboard())
    
    elif callback_data == b'owner_broadcast':
        await event.edit('📢 Broadcast message bhejo\n\n(Feature coming soon...)', buttons=get_back_keyboard())
    
    elif callback_data == b'owner_status':
        status_text = """📊 BOT STATUS

✅ Bot: Active
⏱️ Uptime: 24 hours
📨 Messages Today: 500
👥 Active Users: 95
💾 Database: Connected"""
        await event.edit(status_text, buttons=get_back_keyboard())
    
    elif callback_data == b'owner_settings':
        await event.edit('⚙️ SETTINGS', buttons=get_settings_keyboard())
    
    elif callback_data == b'user_tools':
        await event.edit('🛠️ Tools (coming soon...)', buttons=get_back_keyboard())
    
    elif callback_data == b'user_profile':
        profile_text = f"""👤 YOUR PROFILE

Name: {sender_obj.first_name}
ID: {sender_obj.id}
Username: @{sender_obj.username if sender_obj.username else 'Not set'}
Status: Active"""
        await event.edit(profile_text, buttons=get_back_keyboard())
    
    elif callback_data == b'user_help':
        help_text = """❓ HELP

/start - Start karo
/hello - Hello bolo
/time - Time dekho
/help - Help message"""
        await event.edit(help_text, buttons=get_back_keyboard())
    
    elif callback_data == b'user_about':
        about_text = """ℹ️ ABOUT BOT

Bot v1.0
Created with Telethon
Simple user & admin panel"""
        await event.edit(about_text, buttons=get_back_keyboard())
    
    elif callback_data == b'user_ban':
        await event.edit('🚫 User ban ho gaya', buttons=get_back_keyboard())
    
    elif callback_data == b'user_unban':
        await event.edit('✅ User unban ho gaya', buttons=get_back_keyboard())
    
    elif callback_data == b'user_info':
        info_text = """ℹ️ USER INFO

ID: 12345
Joined: 2025-01-01
Messages: 50
Status: Active"""
        await event.edit(info_text, buttons=get_users_detail_keyboard())
    
    elif callback_data == b'owner_users_back':
        await event.edit('👥 USERS MANAGEMENT\n\n📊 Total Users: 100\n🚫 Banned Users: 5\n✅ Active Users: 95', buttons=get_users_detail_keyboard())
    
    elif callback_data == b'setting_start_text':
        await event.edit('✍️ Start text customize karo\n\n(Coming soon...)', buttons=get_settings_keyboard())
    
    elif callback_data == b'setting_sudo_force':
        await event.edit('🔄 Sudo-Force settings\n\n(Coming soon...)', buttons=get_settings_keyboard())
    
    elif callback_data == b'setting_handle_group':
        await event.edit('👥 Group handling settings\n\n(Coming soon...)', buttons=get_settings_keyboard())
    
    elif callback_data == b'settings_back':
        await event.edit('⚙️ SETTINGS', buttons=get_settings_keyboard())
    
    elif callback_data == b'back_to_main':
        if is_owner:
            await event.edit('🔐 OWNER PANEL\n\nKya karna hai?', buttons=get_owner_main_keyboard())
        else:
            await event.edit(f'👋 Welcome {sender_obj.first_name}!\n\nKya karna hai?', buttons=get_user_main_keyboard())

@client.on(events.NewMessage(pattern='/hello'))
async def hello_handler(event):
    sender = await event.get_sender()
    await event.respond(f'👋 Hello {sender.first_name}! Aap kaise ho?')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/time'))
async def time_handler(event):
    from datetime import datetime
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d-%m-%Y")
    await event.respond(f'📅 Date: {current_date}\n⏰ Time: {current_time}')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    sender = await event.get_sender()
    
    if sender.id == owner_id:
        help_text = """
🔐 OWNER COMMANDS:
/start - Owner panel
/help - Ye help message
        """
    else:
        help_text = """
👤 USER COMMANDS:
/start - Start karo
/hello - Hello bolo
/time - Current time
/help - Ye help message
        """
    
    await event.respond(help_text)
    raise events.StopPropagation

@client.on(events.NewMessage)
async def echo_handler(event):
    if event.is_private and not event.text.startswith('/'):
        await event.respond(f'📝 Aapne likha: {event.text}')

print('🚀 Bot chal raha hai...')
client.run_until_disconnected()
