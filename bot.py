from telethon import TelegramClient, events
import os

api_id = int(os.getenv('API_ID', '22880380'))
api_hash = os.getenv('API_HASH', '08dae0d98b2dc8f8dc4e6a9ff97a071b')
bot_token = os.getenv('BOT_TOKEN', '8028312869:AAErsD7WmHHw11c2lL2Jdoj_DBU4bqRv_kQ')
owner_id = int(os.getenv('OWNER_ID', '0'))

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def show_owner_panel(event):
    """Owner panel ke liye menu dikhao"""
    menu = """
🔐 OWNER PANEL
================
/users - Active users dekho
/stats - Bot ke statistics
/broadcast - Sab ko message bhejo
/help - Owner commands
    """
    await event.respond(menu)

async def show_user_panel(event, user_name):
    """User panel ke liye menu dikhao"""
    menu = f"""
👋 Welcome {user_name}!
================
/hello - Greeting
/time - Current time
/help - Commands
/echo - Echo mode
    """
    await event.respond(menu)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    
    if sender.id == owner_id:
        await show_owner_panel(event)
    else:
        await show_user_panel(event, sender.first_name or 'User')
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    sender = await event.get_sender()
    
    if sender.id == owner_id:
        help_text = """
🔐 OWNER COMMANDS:
/start - Owner panel
/users - Active users list
/stats - Bot statistics
/broadcast - Message bhejo
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

@client.on(events.NewMessage(pattern='/users'))
async def users_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Ye command sirf owner ko allowed hai!')
        raise events.StopPropagation
    
    await event.respond('👥 Total Users: 100\n\n(Database integration pending)')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/stats'))
async def stats_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Ye command sirf owner ko allowed hai!')
        raise events.StopPropagation
    
    stats_text = """
📊 BOT STATISTICS:
- Total Messages: 500
- Active Users: 100
- Online Now: 50
- Uptime: 24 hours
    """
    await event.respond(stats_text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/broadcast'))
async def broadcast_handler(event):
    sender = await event.get_sender()
    
    if sender.id != owner_id:
        await event.respond('❌ Ye command sirf owner ko allowed hai!')
        raise events.StopPropagation
    
    await event.respond('📢 Broadcast message likho (ye feature soon aayega)')
    raise events.StopPropagation

@client.on(events.NewMessage)
async def echo_handler(event):
    if event.is_private and not event.text.startswith('/'):
        await event.respond(f'📝 Aapne likha: {event.text}')

print('🚀 Bot chal raha hai...')
client.run_until_disconnected()
