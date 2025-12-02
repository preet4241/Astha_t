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
    
    elif data == b'user_ban' or data.startswith(b'ban_page_'):
        # Get page number
        if data == b'user_ban':
            page = 0
        else:
            page = int(data.decode().split('_')[2])
        
        all_users = get_all_users()
        active_users = [u for u in all_users.values() if not u.get('banned', False) and u['user_id'] != owner_id]
        
        if not active_users:
            await event.edit('⚠️ Koi active user nahi hai ban karne ke liye!', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
            return
        
        # Pagination - 6 users per page
        per_page = 6
        total_pages = (len(active_users) + per_page - 1) // per_page
        
        start_idx = page * per_page
        end_idx = min(start_idx + per_page, len(active_users))
        page_users = active_users[start_idx:end_idx]
        
        buttons = []
        for user in page_users:
            btn_text = f"🚫 {user['first_name'][:15]} (@{user['username'][:15]})"
            btn_data = f"action_ban_{user['user_id']}".encode()
            buttons.append([Button.inline(btn_text, btn_data)])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline('◀️ Prev', f'ban_page_{page - 1}'.encode()))
        nav_buttons.append(Button.inline(f'📄 {page + 1}/{total_pages}', b'page_info'))
        if page < total_pages - 1:
            nav_buttons.append(Button.inline('Next ▶️', f'ban_page_{page + 1}'.encode()))
        
        buttons.append(nav_buttons)
        buttons.append([Button.inline('⬅️ Back', b'owner_users')])
        
        await event.edit('🚫 BAN USER\n\n━━━━━━━━━━━━━━━━\nUser select karo:', buttons=buttons)
    
    elif data == b'user_unban' or data.startswith(b'unban_page_'):
        # Get page number
        if data == b'user_unban':
            page = 0
        else:
            page = int(data.decode().split('_')[2])
        
        all_users = get_all_users()
        banned_users = [u for u in all_users.values() if u.get('banned', False)]
        
        if not banned_users:
            await event.edit('⚠️ Koi banned user nahi hai!', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
            return
        
        # Pagination - 6 users per page
        per_page = 6
        total_pages = (len(banned_users) + per_page - 1) // per_page
        
        start_idx = page * per_page
        end_idx = min(start_idx + per_page, len(banned_users))
        page_users = banned_users[start_idx:end_idx]
        
        buttons = []
        for user in page_users:
            btn_text = f"✅ {user['first_name'][:15]} (@{user['username'][:15]})"
            btn_data = f"action_unban_{user['user_id']}".encode()
            buttons.append([Button.inline(btn_text, btn_data)])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline('◀️ Prev', f'unban_page_{page - 1}'.encode()))
        nav_buttons.append(Button.inline(f'📄 {page + 1}/{total_pages}', b'page_info'))
        if page < total_pages - 1:
            nav_buttons.append(Button.inline('Next ▶️', f'unban_page_{page + 1}'.encode()))
        
        buttons.append(nav_buttons)
        buttons.append([Button.inline('⬅️ Back', b'owner_users')])
        
        await event.edit('✅ UNBAN USER\n\n━━━━━━━━━━━━━━━━\nUser select karo:', buttons=buttons)
    
    elif data == b'user_info' or data.startswith(b'info_page_'):
        # Get page number
        if data == b'user_info':
            page = 0
        else:
            page = int(data.decode().split('_')[2])
        
        all_users = get_all_users()
        if not all_users:
            await event.edit('⚠️ Koi user nahi hai database mein!', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
            return
        
        # Pagination - 6 users per page
        per_page = 6
        user_list = list(all_users.values())
        total_pages = (len(user_list) + per_page - 1) // per_page
        
        start_idx = page * per_page
        end_idx = min(start_idx + per_page, len(user_list))
        page_users = user_list[start_idx:end_idx]
        
        buttons = []
        for user in page_users:
            status = '✅' if not user.get('banned', False) else '🚫'
            btn_text = f"{status} {user['first_name'][:15]} (@{user['username'][:15]})"
            btn_data = f"action_info_{user['user_id']}".encode()
            buttons.append([Button.inline(btn_text, btn_data)])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline('◀️ Prev', f'info_page_{page - 1}'.encode()))
        nav_buttons.append(Button.inline(f'📄 {page + 1}/{total_pages}', b'page_info'))
        if page < total_pages - 1:
            nav_buttons.append(Button.inline('Next ▶️', f'info_page_{page + 1}'.encode()))
        
        buttons.append(nav_buttons)
        buttons.append([Button.inline('⬅️ Back', b'owner_users')])
        
        await event.edit('ℹ️ USER INFO\n\n━━━━━━━━━━━━━━━━\nUser select karo:', buttons=buttons)
    
    elif data.startswith(b'action_ban_'):
        target_user_id = int(data.decode().split('_')[2])
        user = get_user(target_user_id)
        
        if user and not user['banned']:
            ban_user(target_user_id)
            ban_text = f"""🚫 USER BANNED

━━━━━━━━━━━━━━━━
👤 User Details:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • ID: {target_user_id}
  • Status: 🚫 Banned

━━━━━━━━━━━━━━━━"""
            await event.edit(ban_text, buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
        else:
            await event.edit('❌ User pehle se banned hai ya nahi mila!', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
    
    elif data.startswith(b'action_unban_'):
        target_user_id = int(data.decode().split('_')[2])
        user = get_user(target_user_id)
        
        if user and user['banned']:
            unban_user(target_user_id)
            unban_text = f"""✅ USER UNBANNED

━━━━━━━━━━━━━━━━
👤 User Details:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • ID: {target_user_id}
  • Status: ✅ Active

━━━━━━━━━━━━━━━━"""
            await event.edit(unban_text, buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
        else:
            await event.edit('❌ User banned nahi hai ya nahi mila!', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
    
    elif data.startswith(b'action_info_'):
        target_user_id = int(data.decode().split('_')[2])
        user = get_user(target_user_id)
        
        if user:
            status_emoji = '✅' if not user['banned'] else '🚫'
            status_text = 'Active' if not user['banned'] else 'Banned'
            
            info_text = f"""ℹ️ USER INFORMATION

━━━━━━━━━━━━━━━━
👤 Profile:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • User ID: {user['user_id']}

📊 Activity:
  • Messages: {user['messages']}
  • Joined: {user['joined'][:10]}
  • Status: {status_emoji} {status_text}

━━━━━━━━━━━━━━━━"""
            
            buttons = []
            if user['banned']:
                buttons.append([Button.inline('✅ Unban User', f'action_unban_{target_user_id}'.encode())])
            else:
                buttons.append([Button.inline('🚫 Ban User', f'action_ban_{target_user_id}'.encode())])
            buttons.append([Button.inline('⬅️ Back', b'owner_users')])
            
            await event.edit(info_text, buttons=buttons)
        else:
            await event.edit('❌ User nahi mila!', buttons=[[Button.inline('⬅️ Back', b'owner_users')]])
    
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
    
    elif data == b'page_info':
        # Just ignore - this is the page number display button
        await event.answer('📄 Page Information', alert=False)
    
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

@client.on(events.NewMessage(pattern='/ban'))
async def ban_command_handler(event):
    sender = await event.get_sender()
    if sender.id != owner_id:
        await event.respond('❌ Sirf owner hi ban kar sakta hai!')
        raise events.StopPropagation
    
    # Check if replying to a message
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        target_user_id = replied_msg.sender_id
    else:
        args = event.text.split()
        if len(args) < 2:
            await event.respond('⚠️ Usage: /ban <user_id/username>\n\nExample: /ban 123456789 ya /ban @username\n\nYa kisi ke message ko reply karke /ban likhiye')
            raise events.StopPropagation
        
        # Check if username or user_id
        target_str = args[1].replace('@', '')
        all_users = get_all_users()
        target_user_id = None
        
        # Try to find by user_id first
        try:
            uid = int(target_str)
            if get_user(uid):
                target_user_id = uid
        except ValueError:
            # Search by username
            for u in all_users.values():
                if u['username'].lower() == target_str.lower():
                    target_user_id = u['user_id']
                    break
        
        if not target_user_id:
            await event.respond(f'❌ User "{args[1]}" database mein nahi mila!')
            raise events.StopPropagation
    
    user = get_user(target_user_id)
    if not user:
        await event.respond(f'❌ User database mein nahi mila!')
        raise events.StopPropagation
    
    if user['banned']:
        await event.respond(f'⚠️ User {user["first_name"]} (@{user["username"]}) pehle se banned hai!')
        raise events.StopPropagation
    
    ban_user(target_user_id)
    ban_text = f"""🚫 USER BANNED

━━━━━━━━━━━━━━━━
👤 User Details:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • ID: {target_user_id}
  • Status: 🚫 Banned

━━━━━━━━━━━━━━━━"""
    await event.respond(ban_text)
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unban'))
async def unban_command_handler(event):
    sender = await event.get_sender()
    if sender.id != owner_id:
        await event.respond('❌ Sirf owner hi unban kar sakta hai!')
        raise events.StopPropagation
    
    args = event.text.split()
    
    # Check if replying to a message
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        target_user_id = replied_msg.sender_id
        user = get_user(target_user_id)
        
        if not user:
            await event.respond(f'❌ User database mein nahi mila!')
            raise events.StopPropagation
        
        if not user['banned']:
            await event.respond(f'⚠️ User {user["first_name"]} (@{user["username"]}) banned nahi hai!')
            raise events.StopPropagation
        
        unban_user(target_user_id)
        unban_text = f"""✅ USER UNBANNED

━━━━━━━━━━━━━━━━
👤 User Details:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • ID: {target_user_id}
  • Status: ✅ Active

━━━━━━━━━━━━━━━━"""
        await event.respond(unban_text)
        raise events.StopPropagation
    
    # Show list if no argument provided
    if len(args) < 2:
        all_users = get_all_users()
        banned_users = [u for u in all_users.values() if u.get('banned', False)]
        
        if not banned_users:
            await event.respond('⚠️ Koi banned user nahi hai!')
            raise events.StopPropagation
        
        # Pagination - 6 users per page
        page = 0
        per_page = 6
        total_pages = (len(banned_users) + per_page - 1) // per_page
        
        start_idx = page * per_page
        end_idx = min(start_idx + per_page, len(banned_users))
        page_users = banned_users[start_idx:end_idx]
        
        list_text = f"""✅ BANNED USERS LIST

━━━━━━━━━━━━━━━━
📄 Page {page + 1}/{total_pages} | Total: {len(banned_users)}

"""
        for i, user in enumerate(page_users, start=start_idx + 1):
            list_text += f"{i}. {user['first_name']} (@{user['username']})\n   ID: {user['user_id']}\n\n"
        
        list_text += "━━━━━━━━━━━━━━━━\n"
        list_text += "Usage: /unban <user_id/username>\nYa message ko reply karke /unban"
        
        # Add pagination buttons
        buttons = []
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline('◀️ Previous', f'unban_page_{page - 1}'.encode()))
        if page < total_pages - 1:
            nav_buttons.append(Button.inline('Next ▶️', f'unban_page_{page + 1}'.encode()))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        await event.respond(list_text, buttons=buttons if buttons else None)
        raise events.StopPropagation
    
    # Unban specific user by ID or username
    target_str = args[1].replace('@', '')
    all_users = get_all_users()
    target_user_id = None
    
    # Try to find by user_id first
    try:
        uid = int(target_str)
        if get_user(uid):
            target_user_id = uid
    except ValueError:
        # Search by username
        for u in all_users.values():
            if u['username'].lower() == target_str.lower():
                target_user_id = u['user_id']
                break
    
    if not target_user_id:
        await event.respond(f'❌ User "{args[1]}" database mein nahi mila!')
        raise events.StopPropagation
    
    user = get_user(target_user_id)
    if not user['banned']:
        await event.respond(f'⚠️ User {user["first_name"]} (@{user["username"]}) banned nahi hai!')
        raise events.StopPropagation
    
    unban_user(target_user_id)
    unban_text = f"""✅ USER UNBANNED

━━━━━━━━━━━━━━━━
👤 User Details:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • ID: {target_user_id}
  • Status: ✅ Active

━━━━━━━━━━━━━━━━"""
    await event.respond(unban_text)
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/info'))
async def info_command_handler(event):
    sender = await event.get_sender()
    if sender.id != owner_id:
        await event.respond('❌ Sirf owner hi user info dekh sakta hai!')
        raise events.StopPropagation
    
    # Check if replying to a message
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        target_user_id = replied_msg.sender_id
    else:
        args = event.text.split()
        if len(args) < 2:
            await event.respond('⚠️ Usage: /info <user_id/username>\n\nExample: /info 123456789 ya /info @username\n\nYa kisi ke message ko reply karke /info likhiye')
            raise events.StopPropagation
        
        # Check if username or user_id
        target_str = args[1].replace('@', '')
        all_users = get_all_users()
        target_user_id = None
        
        # Try to find by user_id first
        try:
            uid = int(target_str)
            if get_user(uid):
                target_user_id = uid
        except ValueError:
            # Search by username
            for u in all_users.values():
                if u['username'].lower() == target_str.lower():
                    target_user_id = u['user_id']
                    break
        
        if not target_user_id:
            await event.respond(f'❌ User "{args[1]}" database mein nahi mila!')
            raise events.StopPropagation
    
    user = get_user(target_user_id)
    if not user:
        await event.respond(f'❌ User database mein nahi mila!')
        raise events.StopPropagation
    
    status_emoji = '✅' if not user['banned'] else '🚫'
    status_text = 'Active' if not user['banned'] else 'Banned'
    
    info_text = f"""ℹ️ USER INFORMATION

━━━━━━━━━━━━━━━━
👤 Profile:
  • Name: {user['first_name']}
  • Username: @{user['username']}
  • User ID: {user['user_id']}

📊 Activity:
  • Messages: {user['messages']}
  • Joined: {user['joined'][:10]}
  • Status: {status_emoji} {status_text}

━━━━━━━━━━━━━━━━"""
    
    buttons = []
    if user['banned']:
        buttons.append([Button.inline('✅ Unban User', f'action_unban_{target_user_id}'.encode())])
    else:
        buttons.append([Button.inline('🚫 Ban User', f'action_ban_{target_user_id}'.encode())])
    
    await event.respond(info_text, buttons=buttons)
    
    raise events.StopPropagation

@client.on(events.NewMessage)
async def message_handler(event):
    sender = await event.get_sender()
    if event.is_private and not event.text.startswith('/'):
        user = get_user(sender.id)
        if user and user.get('banned', False):
            await event.respond('🚫 Aap banned hain! Bot use nahi kar sakte.')
            return
        
        increment_messages(sender.id)
        await event.respond(f'📝 {event.text}')

print('🚀 Bot chal raha hai...')
client.run_until_disconnected()
