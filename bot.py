from telethon import TelegramClient, events, Button
import os
import datetime
from datetime import datetime, timedelta
from users_db import (
    add_user, get_user, ban_user, unban_user, 
    get_all_users, get_stats, increment_messages,
    set_setting, get_setting, add_channel, remove_channel,
    get_all_channels, channel_exists, deactivate_expired_channels,
    check_channel_limits
)

api_id = int(os.getenv('API_ID', '22880380'))
api_hash = os.getenv('API_HASH', '08dae0d98b2dc8f8dc4e6a9ff97a071b')
bot_token = os.getenv('BOT_TOKEN', '8028312869:AAErsD7WmHHw11c2lL2Jdoj_DBU4bqRv_kQ')
owner_id = int(os.getenv('OWNER_ID', '0'))

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

broadcast_temp = {}
start_text_temp = {}
channel_action_temp = {}
channel_page_temp = {}
channel_temp = {}

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

def get_default_owner_text():
    """Default owner start text"""
    return """{greeting} Boss 👑

🤖 Status: 🟢 Active
👥 Users: {total_users} | ✅ Active: {active_users}

━━━━━━━━━━━━━━━━
Your Control Desk:"""

def get_default_user_text():
    """Default user start text"""
    return """{greeting} {first_name}! 👋
━━━━━━━━━━━━━━━━


async def handle_channel_addition(event, sender):
    """Handle multi-step channel addition process"""
    from datetime import timedelta
    import re
    
    step_data = channel_temp[sender.id]
    step = step_data.get('step')
    
    # Step 1: Get channel info
    if step == 'channel_info':
        try:
            # Check if it's a forwarded message
            if event.forward:
                if event.forward.chat:
                    channel_entity = await client.get_entity(event.forward.chat)
                    channel_id = channel_entity.id
                    channel_username = channel_entity.username or str(channel_id)
                    channel_title = channel_entity.title
                    channel_link = f"https://t.me/{channel_username}" if channel_entity.username else f"https://t.me/c/{str(channel_id)[4:]}"
                else:
                    await event.respond("⚠️ Invalid forward! Please forward from a channel.")
                    return
            else:
                # Text input - username or link
                ch_input = event.text.strip()
                ch_name = ch_input.replace('@', '').replace('https://t.me/', '').replace('https://telegram.me/', '')
                
                try:
                    channel_entity = await client.get_entity(ch_name)
                    channel_id = channel_entity.id
                    channel_username = channel_entity.username or str(channel_id)
                    channel_title = channel_entity.title
                    channel_link = f"https://t.me/{channel_username}" if channel_entity.username else f"https://t.me/c/{str(channel_id)[4:]}"
                except Exception as e:
                    await event.respond(f"⚠️ Channel not found!\n\nError: {str(e)}\n\nPlease try again with valid username/link.")
                    return
            
            if channel_exists(channel_username):
                buttons = [[Button.inline('⬅️ Back', b'setting_sub_force')]]
                await event.respond(f'⚠️ Channel already added!\n\n@{channel_username}', buttons=buttons)
                channel_temp[sender.id] = None
                return
            
            # Save channel info
            channel_temp[sender.id] = {
                'step': 'join_limit',
                'username': channel_username,
                'title': channel_title,
                'link': channel_link,
                'id': channel_id
            }
            
            buttons = [[Button.inline('❌ Cancel', b'setting_sub_force')]]
            await event.respond(f"""✅ Channel Details Fetched!

📌 Channel: {channel_title}
🔗 Link: {channel_link}
👤 Username: @{channel_username}

━━━━━━━━━━━━━━━━

➕ ADD CHANNEL - STEP 2/3

📊 How many users must join this channel?
  • Enter a number (e.g., 100, 500)
  • Enter 0 for unlimited (∞)

Type the number:""", buttons=buttons)
            
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}\n\nPlease try again.")
            channel_temp[sender.id] = None
    
    # Step 2: Get join limit
    elif step == 'join_limit':
        try:
            join_limit = int(event.text.strip())
            if join_limit < 0:
                await event.respond("⚠️ Please enter a positive number or 0 for unlimited.")
                return
            
            step_data['join_limit'] = join_limit
            step_data['step'] = 'expiry_time'
            channel_temp[sender.id] = step_data
            
            buttons = [[Button.inline('❌ Cancel', b'setting_sub_force')]]
            limit_text = f"{join_limit} users" if join_limit > 0 else "Unlimited (∞)"
            await event.respond(f"""✅ Join Limit Set: {limit_text}

━━━━━━━━━━━━━━━━

➕ ADD CHANNEL - STEP 3/3

⏰ Set Time Limit (Optional):
  • 1d = 1 day
  • 1w = 1 week
  • 1m = 1 month
  • 30min = 30 minutes

  • Enter 0 or 'none' for permanent

Examples: 7d, 2w, 3m, 120min

Type the time duration:""", buttons=buttons)
            
        except ValueError:
            await event.respond("⚠️ Invalid number! Please enter a valid number.")
    
    # Step 3: Get expiry time
    elif step == 'expiry_time':
        try:
            time_input = event.text.strip().lower()
            expiry_date = None
            duration_text = "Permanent"
            
            if time_input not in ['0', 'none', '']:
                # Parse time duration
                match = re.match(r'(\d+)(d|w|m|min)', time_input)
                if not match:
                    await event.respond("⚠️ Invalid format!\n\nUse: 1d, 1w, 1m, 30min")
                    return
                
                amount = int(match.group(1))
                unit = match.group(2)
                
                current_time = datetime.now()
                if unit == 'd':
                    expiry_date = current_time + timedelta(days=amount)
                    duration_text = f"{amount} day(s)"
                elif unit == 'w':
                    expiry_date = current_time + timedelta(weeks=amount)
                    duration_text = f"{amount} week(s)"
                elif unit == 'm':
                    expiry_date = current_time + timedelta(days=amount*30)
                    duration_text = f"{amount} month(s)"
                elif unit == 'min':
                    expiry_date = current_time + timedelta(minutes=amount)
                    duration_text = f"{amount} minute(s)"
                
                expiry_date = expiry_date.isoformat() if expiry_date else None
            
            # Save channel to database
            username = step_data['username']
            title = step_data['title']
            link = step_data['link']
            join_limit = step_data['join_limit']
            
            add_channel(username, title, link, join_limit, expiry_date)
            
            limit_text = f"{join_limit} users" if join_limit > 0 else "Unlimited (∞)"
            
            buttons = [[Button.inline('⬅️ Back to Settings', b'setting_sub_force')]]
            await event.respond(f"""✅ CHANNEL ADDED SUCCESSFULLY!

━━━━━━━━━━━━━━━━
📌 Channel: {title}
🔗 Link: {link}
👤 Username: @{username}

📊 Settings:
  • Join Limit: {limit_text}
  • Duration: {duration_text}

━━━━━━━━━━━━━━━━
Users must now join this channel to use the bot!""", buttons=buttons)
            
            channel_temp[sender.id] = None
            
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}\n\nPlease try again.")
            channel_temp[sender.id] = None


What would you like to do?"""

def format_text(text, sender, stats, user=None):
    """Format text with placeholders"""
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    current_datetime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    user_messages = 0
    joined_date = "Unknown"
    if user:
        user_messages = user.get('messages', 0)
        joined_date = user.get('joined', 'Unknown')[:10]
    
    return text.format(
        greeting=get_greeting(),
        first_name=sender.first_name or 'User',
        username=sender.username or 'user',
        user_id=sender.id,
        total_users=stats['total_users'],
        active_users=stats['active_users'],
        banned_users=stats['banned_users'],
        total_messages=stats['total_messages'],
        date=current_date,
        time=current_time,
        datetime=current_datetime,
        user_messages=user_messages,
        joined_date=joined_date,
        bot_name='MultiBot'
    )

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
    
    stats = get_stats()
    
    if sender.id == owner_id:
        buttons = [
            [Button.inline('🛠️ Tools', b'owner_tools')],
            [Button.inline('👥 Users', b'owner_users'), Button.inline('📢 Broadcast', b'owner_broadcast')],
            [Button.inline('📊 Status', b'owner_status'), Button.inline('⚙️ Settings', b'owner_settings')],
        ]
        custom_text = get_setting('owner_start_text', get_default_owner_text())
        owner_text = format_text(custom_text, sender, stats, None)
        await event.respond(owner_text, buttons=buttons)
    else:
        buttons = [
            [Button.inline('🛠️ Tools', b'user_tools')],
            [Button.inline('👤 Profile', b'user_profile'), Button.inline('❓ Help', b'user_help')],
            [Button.inline('ℹ️ About', b'user_about')],
        ]
        user_data = get_user(sender.id)
        custom_text = get_setting('user_start_text', get_default_user_text())
        user_text = format_text(custom_text, sender, stats, user_data)
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
            [Button.inline('📱 Sub-Force', b'setting_sub_force'), Button.inline('👥 Groups', b'setting_groups')],
            [Button.inline('⬅️ Back', b'owner_back')],
        ]
        settings_text = """⚙️ BOT SETTINGS

━━━━━━━━━━━━━━━━
Configure your bot behavior and features:

✍️ Start Text - Customize welcome message
📱 Sub-Force - Manage required channels
👥 Groups - Handle group messages

━━━━━━━━━━━━━━━━"""
        await event.edit(settings_text, buttons=buttons)
    
    elif data == b'setting_start_text':
        buttons = [
            [Button.inline('👑 Owner', b'start_text_owner'), Button.inline('👤 User', b'start_text_user')],
            [Button.inline('⬅️ Back', b'owner_settings')],
        ]
        await event.edit('✍️ START TEXT\n\n━━━━━━━━━━━━━━━━\nChoose which text to customize:', buttons=buttons)
    
    elif data == b'start_text_owner':
        buttons = [
            [Button.inline('✏️ Edit', b'start_text_owner_edit'), Button.inline('👁️ See', b'start_text_owner_see')],
            [Button.inline('🔄 Default', b'start_text_owner_default')],
            [Button.inline('⬅️ Back', b'setting_start_text')],
        ]
        await event.edit('👑 OWNER START TEXT\n\n━━━━━━━━━━━━━━━━\nWhat do you want to do?', buttons=buttons)
    
    elif data == b'start_text_user':
        buttons = [
            [Button.inline('✏️ Edit', b'start_text_user_edit'), Button.inline('👁️ See', b'start_text_user_see')],
            [Button.inline('🔄 Default', b'start_text_user_default')],
            [Button.inline('⬅️ Back', b'setting_start_text')],
        ]
        await event.edit('👤 USER START TEXT\n\n━━━━━━━━━━━━━━━━\nWhat do you want to do?', buttons=buttons)
    
    elif data == b'start_text_owner_edit':
        start_text_temp[sender.id] = 'owner'
        buttons = [[Button.inline('❌ Cancel', b'start_text_owner')]]
        help_text = """✏️ Type new start text for Owner:

🎯 OWNER PLACEHOLDERS:
{greeting} - Good Morning/Afternoon/Evening/Night
{date} - Current date (DD-MM-YYYY)
{time} - Current time (HH:MM:SS)
{datetime} - Full date & time
{total_users} - Total users count
{active_users} - Active users count
{banned_users} - Banned users count
{total_messages} - Total messages sent
{bot_name} - Bot name

Example:
{greeting} Boss 👑

🤖 Status: Active
👥 Users: {total_users}
📊 Messages: {total_messages}"""
        await event.edit(help_text, buttons=buttons)
    
    elif data == b'start_text_user_edit':
        start_text_temp[sender.id] = 'user'
        buttons = [[Button.inline('❌ Cancel', b'start_text_user')]]
        help_text = """✏️ Type new start text for User:

👤 USER PLACEHOLDERS:
{greeting} - Good Morning/Afternoon/Evening/Night
{first_name} - User's first name
{username} - User's username
{user_id} - User's ID
{date} - Current date (DD-MM-YYYY)
{time} - Current time (HH:MM:SS)
{datetime} - Full date & time
{user_messages} - User's message count
{joined_date} - Date user joined
{total_users} - Total community users
{bot_name} - Bot name

Example:
{greeting} {first_name}! 👋
━━━━━━━━━━━━━━━━
Joined: {joined_date}
Messages: {user_messages}"""
        await event.edit(help_text, buttons=buttons)
    
    elif data == b'start_text_owner_see':
        owner_text = get_setting('owner_start_text', get_default_owner_text())
        preview = format_text(owner_text, sender, get_stats(), None)
        see_text = f"👑 OWNER START TEXT\n\n━━━━━━━━━━━━━━━━\n{preview}\n\n━━━━━━━━━━━━━━━━\n📌 Placeholders:\n{{greeting}}, {{date}}, {{time}}, {{total_users}}, {{active_users}}, {{banned_users}}, {{total_messages}}, {{bot_name}}"
        await event.edit(see_text, buttons=[[Button.inline('⬅️ Back', b'start_text_owner')]])
    
    elif data == b'start_text_user_see':
        user_text = get_setting('user_start_text', get_default_user_text())
        user_data = get_user(sender.id)
        preview = format_text(user_text, sender, get_stats(), user_data)
        see_text = f"👤 USER START TEXT\n\n━━━━━━━━━━━━━━━━\n{preview}\n\n━━━━━━━━━━━━━━━━\n📌 Placeholders:\n{{greeting}}, {{first_name}}, {{username}}, {{date}}, {{user_messages}}, {{joined_date}}, {{total_users}}, {{bot_name}}"
        await event.edit(see_text, buttons=[[Button.inline('⬅️ Back', b'start_text_user')]])
    
    elif data == b'start_text_owner_default':
        set_setting('owner_start_text', get_default_owner_text())
        await event.edit('👑 Reset to default Owner start text\n\n✅ Confirmed', buttons=[[Button.inline('⬅️ Back', b'start_text_owner')]])
    
    elif data == b'start_text_user_default':
        set_setting('user_start_text', get_default_user_text())
        await event.edit('👤 Reset to default User start text\n\n✅ Confirmed', buttons=[[Button.inline('⬅️ Back', b'start_text_user')]])
    
    elif data == b'setting_sub_force':
        channels = get_all_channels()
        buttons = [
            [Button.inline('➕ Add', b'sub_force_add'), Button.inline('➖ Remove', b'sub_force_remove')],
            [Button.inline('📋 List', b'sub_force_list_page_1')],
            [Button.inline('⬅️ Back', b'owner_settings')],
        ]
        sub_text = f"""📱 SUB-FORCE (Channel Subscription Enforcement)

━━━━━━━━━━━━━━━━
📊 Active Channels: {len(channels)}

Connected channels that users MUST join to use the bot.

What would you like to do?"""
        await event.edit(sub_text, buttons=buttons)
    
    elif data == b'sub_force_add':
        channel_temp[sender.id] = {'step': 'channel_info'}
        buttons = [[Button.inline('❌ Cancel', b'setting_sub_force')]]
        await event.edit("""➕ ADD CHANNEL - STEP 1/3

📌 Send Channel Information:
  • Channel Username (e.g., @mychannel)
  • Channel Link (e.g., https://t.me/mychannel)
  • Forward a message from the channel

Any of these methods will work!""", buttons=buttons)
    
    elif data == b'sub_force_remove':
        channels = get_all_channels()
        if not channels:
            await event.edit('📭 No channels to remove!\n\nAdd channels first.', buttons=[[Button.inline('⬅️ Back', b'setting_sub_force')]])
        else:
            channel_page_temp[sender.id] = 1
            total_pages = (len(channels) + 5) // 6
            start_idx = 0
            end_idx = min(6, len(channels))
            buttons = []
            for ch in channels[start_idx:end_idx]:
                buttons.append([Button.inline(f'❌ {ch["username"]}', f'remove_ch_{ch["channel_id"]}')]) 
            if total_pages > 1:
                buttons.append([Button.inline(f'➡️ Next (1/{total_pages})', b'sub_force_remove_next')])
            buttons.append([Button.inline('⬅️ Back', b'setting_sub_force')])
            await event.edit('➖ REMOVE CHANNEL\n\nSelect channel to remove:', buttons=buttons)
    
    elif data == b'sub_force_remove_next':
        channels = get_all_channels()
        page = channel_page_temp.get(sender.id, 1) + 1
        total_pages = (len(channels) + 5) // 6
        if page > total_pages:
            page = 1
        channel_page_temp[sender.id] = page
        start_idx = (page - 1) * 6
        end_idx = min(start_idx + 6, len(channels))
        buttons = []
        for ch in channels[start_idx:end_idx]:
            buttons.append([Button.inline(f'❌ {ch["username"]}', f'remove_ch_{ch["channel_id"]}')])
        if total_pages > 1:
            buttons.append([Button.inline(f'➡️ Next ({page}/{total_pages})', b'sub_force_remove_next')])
        buttons.append([Button.inline('⬅️ Back', b'setting_sub_force')])
        await event.edit('➖ REMOVE CHANNEL\n\nSelect channel to remove:', buttons=buttons)
    
    elif data.startswith(b'remove_ch_'):
        channel_id = int(data.split(b'_')[2])
        channels = get_all_channels()
        for ch in channels:
            if ch['channel_id'] == channel_id:
                remove_channel(ch['username'])
                await event.edit(f'✅ Channel {ch["username"]} removed!', buttons=[[Button.inline('⬅️ Back', b'setting_sub_force')]])
                break
    
    elif data == b'sub_force_list_page_1' or data.startswith(b'sub_force_list_page_'):
        channels = get_all_channels()
        if not channels:
            await event.edit('📭 No channels added yet!', buttons=[[Button.inline('⬅️ Back', b'setting_sub_force')]])
        else:
            if data.startswith(b'sub_force_list_page_'):
                page = int(data.split(b'_')[3])
            else:
                page = 1
            total_pages = (len(channels) + 5) // 6
            start_idx = (page - 1) * 6
            end_idx = min(start_idx + 6, len(channels))
            
            text = f"📋 CHANNELS LIST (Page {page}/{total_pages})\n\n━━━━━━━━━━━━━━━━\n"
            for i, ch in enumerate(channels[start_idx:end_idx], 1):
                added = ch['added_date'][:10] if ch['added_date'] else 'Unknown'
                text += f"{i}. @{ch['username']}\n"
                text += f"   📌 {ch['title']}\n"
                text += f"   📅 Added: {added}\n\n"
            
            buttons = []
            if page > 1:
                buttons.append([Button.inline(f'⬅️ Prev ({page}/{total_pages})', f'sub_force_list_page_{page-1}'.encode())])
            if page < total_pages:
                buttons.append([Button.inline(f'➡️ Next ({page}/{total_pages})', f'sub_force_list_page_{page+1}'.encode())])
            buttons.append([Button.inline('⬅️ Back', b'setting_sub_force')])
            await event.edit(text, buttons=buttons)
    
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
Your Control Desk:"""
        await event.edit(owner_text, buttons=buttons)
    
    elif data == b'user_back':
        buttons = [
            [Button.inline('🛠️ Tools', b'user_tools')],
            [Button.inline('👤 Profile', b'user_profile'), Button.inline('❓ Help', b'user_help')],
            [Button.inline('ℹ️ About', b'user_about')],
        ]
        greeting = get_greeting()
        user_text = f"""{greeting} {sender.first_name}! 👋
━━━━━━━━━━━━━━━━
What would you like to do?"""
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
    
    if channel_temp.get(sender.id):
        await handle_channel_addition(event, sender)
        raise events.StopPropagation
    
    if start_text_temp.get(sender.id):
        text_type = start_text_temp[sender.id]
        message = event.text
        
        if text_type == 'owner':
            set_setting('owner_start_text', message)
            start_text_temp[sender.id] = None
            preview = format_text(message, sender, get_stats())
            buttons = [[Button.inline('⬅️ Back', b'start_text_owner')]]
            await event.respond(f"✅ Owner start text saved!\n\nPreview:\n{preview}", buttons=buttons)
        elif text_type == 'user':
            set_setting('user_start_text', message)
            start_text_temp[sender.id] = None
            preview = format_text(message, sender, get_stats())
            buttons = [[Button.inline('⬅️ Back', b'start_text_user')]]
            await event.respond(f"✅ User start text saved!\n\nPreview:\n{preview}", buttons=buttons)
        
        raise events.StopPropagation
    
    elif broadcast_temp.get(sender.id):
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
        raise events.StopPropagation
    
    elif event.is_private and not event.text.startswith('/'):
        increment_messages(sender.id)
        await event.respond(f'📝 {event.text}')

print('🚀 Bot chal raha hai...')
client.run_until_disconnected()
