from telethon import TelegramClient, events

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond('Namaste! Main aapka bot hoon. Kaise madad kar sakta hoon?')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    help_text = """
Available Commands:
/start - Bot ko start karo
/help - Ye help message dekho
/hello - Hello bolo
/time - Current time dekho
    """
    await event.respond(help_text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/hello'))
async def hello_handler(event):
    sender = await event.get_sender()
    await event.respond(f'Hello {sender.first_name}! Aap kaise ho?')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/time'))
async def time_handler(event):
    from datetime import datetime
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d-%m-%Y")
    await event.respond(f'Date: {current_date}\nTime: {current_time}')
    raise events.StopPropagation

@client.on(events.NewMessage)
async def echo_handler(event):
    if event.is_private and not event.text.startswith('/'):
        await event.respond(f'Aapne likha: {event.text}')

print('Bot chal raha hai...')
client.run_until_disconnected()
