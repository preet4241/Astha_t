# -*- coding: utf-8 -*-
from telethon import TelegramClient, events, Button
import os
import random
from datetime import datetime, timedelta
from database import (
    add_user, get_user, ban_user, unban_user, 
    get_all_users, get_stats, increment_messages,
    set_setting, get_setting, add_channel, remove_channel,
    get_all_channels, channel_exists, add_group, remove_group,
    get_all_groups, group_exists
)

api_id = int(os.getenv('API_ID', '22880380'))
api_hash = os.getenv('API_HASH', '08dae0d98b2dc8f8dc4e6a9ff97a071b')
bot_token = os.getenv('BOT_TOKEN', '8028312869:AAErsD7WmHHw11c2lL2Jdoj_DBU4bqRv_kQ')
owner_id = int(os.getenv('OWNER_ID', '8267410570'))

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

broadcast_temp = {}
start_text_temp = {}
channel_action_temp = {}
channel_page_temp = {}
group_action_temp = {}
group_page_temp = {}
user_action_temp = {}
user_action_type = {}

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"

def get_default_owner_text():
    return "{greeting} Boss\n\nBOT Status: Online\nUsers: {total_users} | Active: {active_users}\n\nControl Desk:"

def get_default_user_text():
    return "{greeting} {first_name}!\n\nWhat would you like to do?"

def get_default_welcome_messages():
    """Return list of default welcome messages for groups"""
    return [
        "Welcome to the hall of fame, @{username}! {group_name} honors you! 🏛️",
        "🎉 A warm welcome to @{username}! {group_name} is now more awesome with you here!",
        "🌟 Welcome aboard, @{username}! {group_name} welcomes you with open arms!",
        "👋 Hey @{username}! {group_name} is thrilled to have you join us!",
        "🎊 Welcome to paradise, @{username}! {group_name} just got better!",
        "✨ Greetings @{username}! {group_name} is honored by your presence!",
        "🎭 Welcome to the show, @{username}! {group_name} is ready to entertain you!",
        "🚀 Blast off into @{username}! {group_name} is taking you on an epic journey!",
        "💎 Welcome precious member @{username}! {group_name} treasures your arrival!",
        "🎪 Step right up, @{username}! {group_name} welcomes you to the greatest show!"
    ]

def get_random_welcome_message(username, group_name):
    """Get a random welcome message"""
    messages = get_default_welcome_messages()
    selected = random.choice(messages)
    return selected.format(username=username, group_name=group_name)

def format_text(text, sender, stats, user=None):
    current_date = datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.now().strftime("%H:%M:%S")
    current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
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
    if not sender:
        return
    add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
    
    user_data = get_user(sender.id)
    if user_data and user_data.get('banned'):
        await event.respond('🚫 You are BANNED from using this bot!')
        raise events.StopPropagation
    
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
        custom_text = get_setting('user_start_text', get_default_user_text())
        user_text = format_text(custom_text, sender, stats, user_data)
        await event.respond(user_text, buttons=buttons)
    
    raise events.StopPropagation

@client.on(events.CallbackQuery)
async def callback_handler(event):
    sender = await event.get_sender()
    if not sender:
        return
    data = event.data
    
    if sender.id != owner_id:
        user_data = get_user(sender.id)
        if user_data and user_data.get('banned'):
            await event.answer("🚫 You are BANNED!", alert=True)
            return
        if not data.startswith(b'user_'):
            await event.answer("Owner only!", alert=True)
            return
    
    if data == b'owner_groups':
        groups = get_all_groups()
        buttons = [
            [Button.inline('➕ Add', b'group_add'), Button.inline('➖ Remove', b'group_remove')],
            [Button.inline('📋 List', b'group_list_page_1'), Button.inline('👋 Welcome', b'group_welcome_text')],
            [Button.inline('🔙 Back', b'owner_back')],
        ]
        group_text = f"GROUPS\n\nConnected: {len(groups)}\n\nWhat do you want to do?"
        await event.edit(group_text, buttons=buttons)
    
    elif data == b'group_welcome_text':
        buttons = [
            [Button.inline('✏️ Edit', b'group_welcome_text_add'), Button.inline('🗑️ Remove', b'group_welcome_text_remove'), Button.inline('🔄 Default', b'group_welcome_text_default')],
            [Button.inline('💬 Messages', b'group_welcome_text_msgs')],
            [Button.inline('🔙 Back', b'owner_groups')],
        ]
        current_text = get_setting('group_welcome_text', 'Welcome to group!')
        text = f"GROUP WELCOME TEXT\n\nCurrent: {current_text}\n\nManage welcome message for new members:"
        await event.edit(text, buttons=buttons)
    
    elif data == b'group_welcome_text_msgs':
        groups = get_all_groups()
        total_groups = len(groups)
        msg_text = f"Total Groups Connected: {total_groups}\n\n"
        for i, grp in enumerate(groups, 1):
            msg_text += f"{i}. {grp['title']}\n"
        buttons = [
            [Button.inline('🔙 Back', b'group_welcome_text')]
        ]
        await event.edit(msg_text, buttons=buttons)
    
    elif data == b'group_welcome_text_add':
        start_text_temp[sender.id] = 'group_welcome'
        buttons = [[Button.inline('❌ Cancel', b'group_welcome_text')]]
        help_text = "Type new group welcome text:\n\nPlaceholders: {greeting}, {date}, {time}, {bot_name}, {first_name}"
        await event.edit(help_text, buttons=buttons)
    
    elif data == b'group_welcome_text_remove':
        set_setting('group_welcome_text', '')
        await event.edit('Group welcome text removed!', buttons=[[Button.inline('🔙 Back', b'group_welcome_text')]])
    
    elif data == b'group_welcome_text_default':
        set_setting('group_welcome_text', '')
        await event.edit('Group welcome text reset to random default messages!', buttons=[[Button.inline('🔙 Back', b'group_welcome_text')]])
    
    elif data == b'group_add':
        group_action_temp[sender.id] = 'add'
        buttons = [[Button.inline('❌ Cancel', b'owner_groups')]]
        await event.edit("ADD GROUP\n\nChoose one method:\n1. Group ID (number)\n2. Group username (@username)\n3. Forward message from group", buttons=buttons)
    
    elif data == b'group_remove':
        groups = get_all_groups()
        if not groups:
            await event.edit('No groups to remove!', buttons=[[Button.inline('🔙 Back', b'owner_groups')]])
        else:
            group_page_temp[sender.id] = 1
            total_pages = (len(groups) + 5) // 6
            start_idx = 0
            end_idx = min(6, len(groups))
            buttons = []
            for grp in groups[start_idx:end_idx]:
                buttons.append([Button.inline(f'❌ {grp["username"]}', f'remove_grp_{grp["group_id"]}')]) 
            if total_pages > 1:
                buttons.append([Button.inline(f'➡️ Next (1/{total_pages})', b'group_remove_next')])
            buttons.append([Button.inline('🔙 Back', b'owner_groups')])
            await event.edit('REMOVE GROUP\n\nSelect group to remove:', buttons=buttons)
    
    elif data == b'group_remove_next':
        groups = get_all_groups()
        page = group_page_temp.get(sender.id, 1) + 1
        total_pages = (len(groups) + 5) // 6
        if page > total_pages:
            page = 1
        group_page_temp[sender.id] = page
        start_idx = (page - 1) * 6
        end_idx = min(start_idx + 6, len(groups))
        buttons = []
        for grp in groups[start_idx:end_idx]:
            buttons.append([Button.inline(f'❌ {grp["username"]}', f'remove_grp_{grp["group_id"]}')]) 
        if total_pages > 1:
            buttons.append([Button.inline(f'➡️ Next ({page}/{total_pages})', b'group_remove_next')])
        buttons.append([Button.inline('🔙 Back', b'owner_groups')])
        await event.edit('REMOVE GROUP\n\nSelect group to remove:', buttons=buttons)
    
    elif data == b'group_list_page_1':
        groups = get_all_groups()
        if not groups:
            await event.edit('No groups yet!', buttons=[[Button.inline('🔙 Back', b'owner_groups')]])
        else:
            group_page_temp[sender.id] = 1
            total_pages = (len(groups) + 5) // 6
            start_idx = 0
            end_idx = min(6, len(groups))
            buttons = []
            for grp in groups[start_idx:end_idx]:
                buttons.append([Button.inline(f'👥 {grp["title"]}', f'show_grp_{grp["group_id"]}')])
            if total_pages > 1:
                buttons.append([Button.inline(f'➡️ Next (1/{total_pages})', b'group_list_next')])
            buttons.append([Button.inline('🔙 Back', b'owner_groups')])
            await event.edit('GROUPS LIST', buttons=buttons)
    
    elif data == b'group_list_next':
        groups = get_all_groups()
        page = group_page_temp.get(sender.id, 1) + 1
        total_pages = (len(groups) + 5) // 6
        if page > total_pages:
            page = 1
        group_page_temp[sender.id] = page
        start_idx = (page - 1) * 6
        end_idx = min(start_idx + 6, len(groups))
        buttons = []
        for grp in groups[start_idx:end_idx]:
            buttons.append([Button.inline(f'👥 {grp["title"]}', f'show_grp_{grp["group_id"]}')])
        if total_pages > 1:
            buttons.append([Button.inline(f'➡️ Next ({page}/{total_pages})', b'group_list_next')])
        buttons.append([Button.inline('🔙 Back', b'owner_groups')])
        await event.edit('GROUPS LIST', buttons=buttons)
    
    elif data.startswith(b'remove_grp_'):
        group_id = int(data.split(b'_')[2])
        remove_group(group_id)
        groups = get_all_groups()
        if not groups:
            await event.edit('All groups removed!', buttons=[[Button.inline('🔙 Back', b'owner_groups')]])
        else:
            total_pages = (len(groups) + 5) // 6
            group_page_temp[sender.id] = 1
            start_idx = 0
            end_idx = min(6, len(groups))
            buttons = []
            for grp in groups[start_idx:end_idx]:
                buttons.append([Button.inline(f'❌ {grp["username"]}', f'remove_grp_{grp["group_id"]}')]) 
            if total_pages > 1:
                buttons.append([Button.inline(f'➡️ Next (1/{total_pages})', b'group_remove_next')])
            buttons.append([Button.inline('🔙 Back', b'owner_groups')])
            await event.edit('REMOVE GROUP\n\nSelect group to remove:', buttons=buttons)
    
    elif data.startswith(b'show_grp_'):
        group_id = int(data.split(b'_')[2])
        groups = get_all_groups()
        grp_info = next((g for g in groups if g['group_id'] == group_id), None)
        if grp_info:
            info_text = f"👥 GROUP: {grp_info['title']}\nID: {grp_info['group_id']}\nUsername: @{grp_info['username']}\nAdded: {grp_info['added_date'][:10]}"
            await event.edit(info_text, buttons=[[Button.inline('🔙 Back', b'group_list_page_1')]])
    
    elif data == b'setting_start_text':
        buttons = [
            [Button.inline('👑 Owner', b'start_text_owner'), Button.inline('👤 User', b'start_text_user')],
            [Button.inline('🔙 Back', b'owner_settings')],
        ]
        await event.edit('START TEXT\n\nChoose which text to customize:', buttons=buttons)
    
    elif data == b'start_text_owner':
        buttons = [
            [Button.inline('✏️ Edit', b'start_text_owner_edit'), Button.inline('👁️ See', b'start_text_owner_see')],
            [Button.inline('🔄 Default', b'start_text_owner_default')],
            [Button.inline('🔙 Back', b'setting_start_text')],
        ]
        await event.edit('OWNER START TEXT\n\nWhat do you want to do?', buttons=buttons)
    
    elif data == b'start_text_user':
        buttons = [
            [Button.inline('✏️ Edit', b'start_text_user_edit'), Button.inline('👁️ See', b'start_text_user_see')],
            [Button.inline('🔄 Default', b'start_text_user_default')],
            [Button.inline('🔙 Back', b'setting_start_text')],
        ]
        await event.edit('USER START TEXT\n\nWhat do you want to do?', buttons=buttons)
    
    elif data == b'start_text_owner_edit':
        start_text_temp[sender.id] = 'owner'
        buttons = [[Button.inline('❌ Cancel', b'start_text_owner')]]
        help_text = "Type new start text for Owner:\n\nPlaceholders: {greeting}, {date}, {time}, {total_users}, {active_users}, {bot_name}"
        await event.edit(help_text, buttons=buttons)
    
    elif data == b'start_text_user_edit':
        start_text_temp[sender.id] = 'user'
        buttons = [[Button.inline('❌ Cancel', b'start_text_user')]]
        help_text = "Type new start text for User:\n\nPlaceholders: {greeting}, {first_name}, {username}, {date}, {user_messages}, {joined_date}"
        await event.edit(help_text, buttons=buttons)
    
    elif data == b'start_text_owner_see':
        owner_text = get_setting('owner_start_text', get_default_owner_text())
        preview = format_text(owner_text, sender, get_stats(), None)
        see_text = f"OWNER START TEXT PREVIEW:\n\n{preview}"
        await event.edit(see_text, buttons=[[Button.inline('🔙 Back', b'start_text_owner')]])
    
    elif data == b'start_text_user_see':
        user_text = get_setting('user_start_text', get_default_user_text())
        user_data = get_user(sender.id)
        preview = format_text(user_text, sender, get_stats(), user_data)
        see_text = f"USER START TEXT PREVIEW:\n\n{preview}"
        await event.edit(see_text, buttons=[[Button.inline('🔙 Back', b'start_text_user')]])
    
    elif data == b'start_text_owner_default':
        set_setting('owner_start_text', get_default_owner_text())
        await event.edit('✅ Owner start text reset to default!\n\nOK', buttons=[[Button.inline('🔙 Back', b'start_text_owner')]])
    
    elif data == b'start_text_user_default':
        set_setting('user_start_text', get_default_user_text())
        await event.edit('✅ User start text reset to default!\n\nOK', buttons=[[Button.inline('🔙 Back', b'start_text_user')]])
    
    elif data == b'setting_sub_force':
        channels = get_all_channels()
        buttons = [
            [Button.inline('➕ Add', b'sub_force_add'), Button.inline('➖ Remove', b'sub_force_remove')],
            [Button.inline('📋 List', b'sub_force_list_page_1')],
            [Button.inline('🔙 Back', b'owner_settings')],
        ]
        sub_text = f"SUB-FORCE (Channel Subscription)\n\nActive Channels: {len(channels)}\n\nWhat do you want to do?"
        await event.edit(sub_text, buttons=buttons)
    
    elif data == b'sub_force_add':
        channel_action_temp[sender.id] = 'add'
        buttons = [[Button.inline('❌ Cancel', b'setting_sub_force')]]
        await event.edit("ADD CHANNEL\n\nChoose one method:\n1. Channel ID (number)\n2. Channel username (@username)\n3. Forward message from channel", buttons=buttons)
    
    elif data == b'sub_force_remove':
        channels = get_all_channels()
        if not channels:
            await event.edit('No channels to remove!', buttons=[[Button.inline('🔙 Back', b'setting_sub_force')]])
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
            buttons.append([Button.inline('🔙 Back', b'setting_sub_force')])
            await event.edit('REMOVE CHANNEL\n\nSelect channel to remove:', buttons=buttons)
    
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
        buttons.append([Button.inline('🔙 Back', b'setting_sub_force')])
        await event.edit('REMOVE CHANNEL\n\nSelect channel to remove:', buttons=buttons)
    
    elif data.startswith(b'remove_ch_'):
        channel_id = int(data.split(b'_')[2])
        channels = get_all_channels()
        for ch in channels:
            if ch['channel_id'] == channel_id:
                remove_channel(ch['username'])
                await event.edit(f'✅ Channel {ch["username"]} removed!', buttons=[[Button.inline('🔙 Back', b'setting_sub_force')]])
                break
    
    elif data == b'sub_force_list_page_1' or data.startswith(b'sub_force_list_page_'):
        channels = get_all_channels()
        if not channels:
            await event.edit('No channels added yet!', buttons=[[Button.inline('🔙 Back', b'setting_sub_force')]])
        else:
            if data.startswith(b'sub_force_list_page_'):
                page = int(data.split(b'_')[3])
            else:
                page = 1
            total_pages = (len(channels) + 5) // 6
            start_idx = (page - 1) * 6
            end_idx = min(start_idx + 6, len(channels))
            
            text = f"📺 CHANNELS LIST (Page {page}/{total_pages})\n\n"
            for i, ch in enumerate(channels[start_idx:end_idx], 1):
                added = ch['added_date'][:10] if ch['added_date'] else 'Unknown'
                text += f"{i}. @{ch['username']}\n"
                text += f"   Title: {ch['title']}\n"
                text += f"   Added: {added}\n\n"
            
            buttons = []
            if page > 1:
                buttons.append([Button.inline(f'⬅️ Prev ({page}/{total_pages})', f'sub_force_list_page_{page-1}'.encode())])
            if page < total_pages:
                buttons.append([Button.inline(f'➡️ Next ({page}/{total_pages})', f'sub_force_list_page_{page+1}'.encode())])
            buttons.append([Button.inline('🔙 Back', b'setting_sub_force')])
            await event.edit(text, buttons=buttons)
    
    elif data == b'owner_settings':
        buttons = [
            [Button.inline('📝 Start Text', b'setting_start_text')],
            [Button.inline('📺 Sub-Force', b'setting_sub_force'), Button.inline('👥 Groups', b'setting_groups')],
            [Button.inline('🔙 Back', b'owner_back')],
        ]
        settings_text = "BOT SETTINGS\n\nConfigure your bot:"
        await event.edit(settings_text, buttons=buttons)
    
    elif data == b'setting_groups':
        groups = get_all_groups()
        buttons = [
            [Button.inline('➕ Add', b'group_add'), Button.inline('➖ Remove', b'group_remove')],
            [Button.inline('📋 List', b'group_list_page_1'), Button.inline('👋 Welcome', b'group_welcome_text')],
            [Button.inline('⚙️ Settings', b'group_setting')],
            [Button.inline('🔙 Back', b'owner_settings')],
        ]
        group_text = f"GROUPS\n\nConnected: {len(groups)}\n\nWhat do you want to do?"
        await event.edit(group_text, buttons=buttons)
    
    elif data == b'group_setting':
        await event.edit('⚙️ Group Settings: Coming soon...', buttons=[[Button.inline('🔙 Back', b'setting_groups')]])
    
    elif data == b'owner_back':
        buttons = [
            [Button.inline('🛠️ Tools', b'owner_tools')],
            [Button.inline('👥 Users', b'owner_users'), Button.inline('📢 Broadcast', b'owner_broadcast')],
            [Button.inline('📊 Status', b'owner_status'), Button.inline('⚙️ Settings', b'owner_settings')],
        ]
        stats = get_stats()
        custom_text = get_setting('owner_start_text', get_default_owner_text())
        owner_text = format_text(custom_text, sender, stats, None)
        await event.edit(owner_text, buttons=buttons)
    
    elif data == b'owner_users':
        buttons = [
            [Button.inline('🚫 Ban', b'user_ban'), Button.inline('✅ Unban', b'user_unban')],
            [Button.inline('ℹ️ Info', b'user_info')],
            [Button.inline('🔙 Back', b'owner_back')],
        ]
        await event.edit('👥 USERS PANEL\n\nChoose an action:', buttons=buttons)
    
    elif data == b'user_ban':
        user_action_type[sender.id] = 'ban'
        buttons = [[Button.inline('❌ Cancel', b'owner_users')]]
        await event.edit('🚫 BAN USER\n\nEnter user ID or username (@username):', buttons=buttons)
    
    elif data == b'user_unban':
        user_action_type[sender.id] = 'unban'
        buttons = [[Button.inline('❌ Cancel', b'owner_users')]]
        await event.edit('✅ UNBAN USER\n\nEnter user ID or username (@username):', buttons=buttons)
    
    elif data == b'user_info':
        user_action_type[sender.id] = 'info'
        buttons = [[Button.inline('❌ Cancel', b'owner_users')]]
        await event.edit('ℹ️ USER INFO\n\nEnter user ID or username (@username):', buttons=buttons)
    
    elif data == b'owner_broadcast':
        buttons = [
            [Button.inline('📤 Send', b'broadcast_send')],
            [Button.inline('🔙 Back', b'owner_back')],
        ]
        await event.edit('📢 BROADCAST\n\nSend message to all users', buttons=buttons)
    
    elif data == b'owner_status':
        stats = get_stats()
        current_time = datetime.now().strftime("%H:%M:%S")
        status_text = f"📊 BOT STATUS\n\nUsers: {stats['total_users']}\nActive: {stats['active_users']}\nMessages: {stats['total_messages']}\nTime: {current_time}"
        buttons = [[Button.inline('🔙 Back', b'owner_back')]]
        await event.edit(status_text, buttons=buttons)
    
    elif data == b'owner_tools':
        await event.edit('🛠️ Tools (coming soon...)', buttons=[[Button.inline('🔙 Back', b'owner_back')]])
    
    elif data == b'user_tools':
        await event.edit('🛠️ User Tools (coming soon...)', buttons=[[Button.inline('🔙 Back', b'user_back')]])
    
    elif data == b'user_profile':
        user = get_user(sender.id)
        if user:
            profile_text = f"👤 Profile\n\nName: {user['first_name']}\nUsername: @{user['username']}\nMessages: {user['messages']}\nJoined: {user['joined'][:10]}"
        else:
            profile_text = "Profile not found"
        await event.edit(profile_text, buttons=[[Button.inline('🔙 Back', b'user_back')]])
    
    elif data == b'user_help':
        await event.edit('❓ Help: Coming soon...', buttons=[[Button.inline('🔙 Back', b'user_back')]])
    
    elif data == b'user_about':
        await event.edit('ℹ️ About: Bot v1.0 by MultiBot', buttons=[[Button.inline('🔙 Back', b'user_back')]])
    
    elif data == b'user_back':
        buttons = [
            [Button.inline('🛠️ Tools', b'user_tools')],
            [Button.inline('👤 Profile', b'user_profile'), Button.inline('❓ Help', b'user_help')],
            [Button.inline('ℹ️ About', b'user_about')],
        ]
        stats = get_stats()
        user_data = get_user(sender.id)
        custom_text = get_setting('user_start_text', get_default_user_text())
        user_text = format_text(custom_text, sender, stats, user_data)
        await event.edit(user_text, buttons=buttons)
    
    elif data == b'broadcast_send':
        broadcast_temp[sender.id] = True
        buttons = [[Button.inline('❌ Cancel', b'owner_back')]]
        await event.edit('📝 Type your broadcast message:', buttons=buttons)

@client.on(events.NewMessage)
async def message_handler(event):
    sender = await event.get_sender()
    if not sender:
        return
    
    if channel_action_temp.get(sender.id) == 'add':
        ch_name = None
        ch_title = None
        
        if event.forward and event.forward.chat:
            try:
                channel_entity = await client.get_entity(event.forward.chat)
                ch_name = channel_entity.username or str(channel_entity.id)
                ch_title = channel_entity.title
            except Exception as e:
                await event.respond(f'Error extracting channel: {str(e)}')
                return
        elif event.text:
            ch_input = event.text.strip()
            if ch_input.isdigit():
                ch_name = ch_input
                ch_title = ch_input
            elif ch_input.startswith('@'):
                ch_name = ch_input[1:]
                ch_title = ch_input[1:]
            else:
                await event.respond('Invalid format. Use: ID number, @username, or forward message.')
                return
        
        if not ch_name:
            await event.respond('Send one of: ID, @username, or forward a message.')
            return
        
        if channel_exists(ch_name):
            buttons = [[Button.inline('Back', b'setting_sub_force')]]
            await event.respond(f'Channel {ch_name} already added!', buttons=buttons)
        else:
            add_channel(ch_name, ch_title)
            channel_action_temp[sender.id] = None
            buttons = [[Button.inline('Back', b'setting_sub_force')]]
            await event.respond(f'Channel {ch_name} added successfully!', buttons=buttons)
        raise events.StopPropagation
    
    if group_action_temp.get(sender.id) == 'add':
        grp_id = None
        grp_name = None
        grp_title = None
        
        if event.forward and event.forward.chat:
            try:
                group_entity = await client.get_entity(event.forward.chat)
                grp_id = group_entity.id
                grp_name = group_entity.username or str(group_entity.id)
                grp_title = group_entity.title
            except Exception as e:
                await event.respond(f'Error extracting group: {str(e)}')
                return
        elif event.text:
            grp_input = event.text.strip()
            if grp_input.isdigit():
                grp_id = int(grp_input)
                grp_name = grp_input
                grp_title = grp_input
            elif grp_input.startswith('@'):
                grp_name = grp_input[1:]
                grp_id = hash(grp_name) % 1000000
                grp_title = grp_input[1:]
            else:
                await event.respond('Invalid format. Use: ID number, @username, or forward message.')
                return
        
        if not grp_id or not grp_name:
            await event.respond('Send one of: ID, @username, or forward a message.')
            return
        
        if group_exists(grp_id):
            buttons = [[Button.inline('Back', b'owner_groups')]]
            await event.respond(f'Group {grp_name} already added!', buttons=buttons)
        else:
            add_group(grp_id, grp_name, grp_title)
            group_action_temp[sender.id] = None
            buttons = [[Button.inline('Back', b'owner_groups')]]
            await event.respond(f'Group {grp_name} added successfully!', buttons=buttons)
        raise events.StopPropagation
    
    if user_action_type.get(sender.id):
        action = user_action_type[sender.id]
        user_input = event.text.strip()
        target_user = None
        
        if user_input.isdigit():
            target_user = get_user(int(user_input))
        elif user_input.startswith('@'):
            username = user_input[1:]
            all_users = get_all_users()
            for uid_str, user in all_users.items():
                if user.get('username') == username:
                    target_user = user
                    break
        else:
            await event.respond('Invalid format. Use: user ID or @username', buttons=[[Button.inline('🔙 Back', b'owner_users')]])
            raise events.StopPropagation
        
        if not target_user:
            await event.respond('❌ User not found!', buttons=[[Button.inline('🔙 Back', b'owner_users')]])
            user_action_type[sender.id] = None
            raise events.StopPropagation
        
        if action == 'ban':
            if target_user.get('banned'):
                await event.respond('❌ This user is already banned!', buttons=[[Button.inline('🔙 Back', b'owner_users')]])
            else:
                ban_user(target_user['user_id'])
                user_action_type[sender.id] = None
                result_text = f"✅ User Banned!\n\nUser ID: {target_user['user_id']}\nUsername: @{target_user['username']}\nName: {target_user['first_name']}"
                buttons = [[Button.inline('🔙 Back', b'owner_users')]]
                await event.respond(result_text, buttons=buttons)
                try:
                    await client.send_message(target_user['user_id'], '🚫 You have been BANNED from this bot. You cannot use any commands or features.')
                except Exception:
                    pass
        
        elif action == 'unban':
            if not target_user.get('banned'):
                await event.respond('❌ This user is not banned!', buttons=[[Button.inline('🔙 Back', b'owner_users')]])
            else:
                unban_user(target_user['user_id'])
                user_action_type[sender.id] = None
                result_text = f"✅ User Unbanned!\n\nUser ID: {target_user['user_id']}\nUsername: @{target_user['username']}\nName: {target_user['first_name']}"
                buttons = [[Button.inline('🔙 Back', b'owner_users')]]
                await event.respond(result_text, buttons=buttons)
                try:
                    await client.send_message(target_user['user_id'], '✅ You have been UNBANNED! You can now use the bot again.')
                except Exception:
                    pass
        
        elif action == 'info':
            user_action_type[sender.id] = None
            info_text = f"ℹ️ USER DETAILS\n\n"
            info_text += f"👤 ID: {target_user['user_id']}\n"
            info_text += f"👤 Username: @{target_user['username']}\n"
            info_text += f"📝 Name: {target_user['first_name']}\n"
            info_text += f"💬 Messages: {target_user['messages']}\n"
            info_text += f"📅 Joined: {target_user['joined'][:10]}\n"
            info_text += f"⏰ Full Join Date: {target_user['joined']}\n"
            info_text += f"🔄 Status: {'🚫 BANNED' if target_user['banned'] else '✅ ACTIVE'}\n"
            info_text += f"📊 User Status: {target_user['status']}\n"
            buttons = [[Button.inline('🔙 Back', b'owner_users')]]
            await event.respond(info_text, buttons=buttons)
        
        raise events.StopPropagation
    
    if start_text_temp.get(sender.id):
        text_type = start_text_temp[sender.id]
        message = event.text
        
        if text_type == 'owner':
            set_setting('owner_start_text', message)
            start_text_temp[sender.id] = None
            preview = format_text(message, sender, get_stats())
            buttons = [[Button.inline('Back', b'start_text_owner')]]
            await event.respond(f"Owner start text saved!\n\nPreview:\n{preview}", buttons=buttons)
        elif text_type == 'user':
            set_setting('user_start_text', message)
            start_text_temp[sender.id] = None
            preview = format_text(message, sender, get_stats())
            buttons = [[Button.inline('Back', b'start_text_user')]]
            await event.respond(f"User start text saved!\n\nPreview:\n{preview}", buttons=buttons)
        elif text_type == 'group_welcome':
            set_setting('group_welcome_text', message)
            start_text_temp[sender.id] = None
            preview = format_text(message, sender, get_stats())
            buttons = [[Button.inline('Back', b'group_welcome_text')]]
            await event.respond(f"Group welcome text saved!\n\nPreview:\n{preview}", buttons=buttons)
        
        raise events.StopPropagation
    
    if broadcast_temp.get(sender.id):
        message = event.text
        all_users = get_all_users()
        stats = get_stats()
        
        sent_count = 0
        failed_count = 0
        
        for user_id_str, user in all_users.items():
            if user.get('banned'):
                continue
            
            try:
                await client.send_message(int(user_id_str), message)
                sent_count += 1
            except Exception:
                failed_count += 1
        
        broadcast_temp[sender.id] = False
        result_text = f"Broadcast Complete!\n\nSent: {sent_count}\nFailed: {failed_count}"
        buttons = [[Button.inline('Back', b'owner_back')]]
        await event.respond(result_text, buttons=buttons)
        raise events.StopPropagation

@client.on(events.ChatAction())
async def chat_action_handler(event):
    try:
        chat = await event.get_chat()
        if hasattr(chat, 'id') and (hasattr(event, 'user_joined') and event.user_joined):
            grp_id = chat.id
            grp_name = chat.username or str(chat.id)
            grp_title = chat.title or 'Unknown'
            
            if not group_exists(grp_id):
                add_group(grp_id, grp_name, grp_title)
            
            user = await event.get_sender()
            if user:
                # Check for custom welcome message first
                welcome_msg = get_setting('group_welcome_text', '')
                if welcome_msg:
                    msg_text = format_text(welcome_msg, user, get_stats())
                    await event.respond(msg_text)
                else:
                    # Use random default welcome message
                    user_username = user.username or user.first_name or "user"
                    random_msg = get_random_welcome_message(user_username, grp_title)
                    await event.respond(random_msg)
    except Exception as e:
        pass
    raise events.StopPropagation

@client.on(events.NewMessage(incoming=True))
async def group_message_handler(event):
    try:
        if event.is_group:
            sender = await event.get_sender()
            
            chat = await event.get_chat()
            grp_id = chat.id
            grp_name = chat.username or str(chat.id)
            grp_title = chat.title or 'Unknown'
            
            # Add group to database if not exists
            if not group_exists(grp_id):
                add_group(grp_id, grp_name, grp_title)
            
            # Track user messages (even for anonymous admins, track the group activity)
            if sender:
                add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
                increment_messages(sender.id)
    except Exception as e:
        print(f"Error in group message handler: {e}")
        pass

async def check_admin_permission(event, sender_id):
    """Check if user has admin permission (bot owner, group owner, or group admin)"""
    # Bot owner has permission everywhere
    if sender_id == owner_id:
        return True
    
    # In private chat, only bot owner allowed
    if event.is_private:
        return False
    
    # In group, check if user is group owner or admin
    if event.is_group:
        try:
            chat = await event.get_chat()
            
            # Check if message is from anonymous admin
            # Anonymous admins have sender_id as the group's linked channel or 1087968824
            if hasattr(event, 'sender_id'):
                # If sender is anonymous admin (136817688 or similar channel-based ID)
                # We need to check the actual user who sent via event.message.from_id
                if event.message and hasattr(event.message, 'from_id'):
                    # For anonymous admins, from_id will be PeerChannel
                    from telethon.tl.types import PeerChannel
                    if isinstance(event.message.from_id, PeerChannel):
                        # This is an anonymous admin, return True
                        print(f"Anonymous admin detected in group {chat.title}")
                        return True
            
            # Regular user permission check
            try:
                participant = await client.get_permissions(chat, sender_id)
                if participant.is_creator or participant.is_admin:
                    return True
            except Exception as perm_error:
                print(f"Permission check error: {perm_error}")
                # Last resort: check if the original sender_id itself indicates admin
                # Sometimes anonymous admins appear with group channel ID
                return False
                
        except Exception as e:
            print(f"Error checking permissions: {e}")
            return False
    
    return False

@client.on(events.NewMessage(pattern=r'/ban(?:\s+(.+))?'))
async def ban_handler(event):
    sender = await event.get_sender()
    if not sender:
        raise events.StopPropagation
    
    # Check admin permission
    has_permission = await check_admin_permission(event, sender.id)
    if not has_permission:
        await event.respond('🔐 Only bot owner or group admins can use this command!')
        raise events.StopPropagation
    
    # Get target user
    target_user_id = None
    target_user = None
    match = event.pattern_match
    
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.from_id:
            target_user_id = reply_msg.from_id.user_id
            target_user = get_user(target_user_id)
    elif match.group(1):
        user_input = match.group(1).strip()
        if user_input.isdigit():
            target_user_id = int(user_input)
            target_user = get_user(target_user_id)
        elif user_input.startswith('@'):
            username = user_input[1:]
            all_users = get_all_users()
            for uid_str, user in all_users.items():
                if user.get('username') == username:
                    target_user = user
                    target_user_id = user['user_id']
                    break
        else:
            await event.respond('❌ Invalid format. Use: `/ban <user_id>` or `/ban @username` or reply with `/ban`')
            raise events.StopPropagation
    else:
        await event.respond('❌ No user specified. Use: `/ban <user_id>` or `/ban @username` or reply with `/ban`')
        raise events.StopPropagation
    
    # In group, verify target user is in the same group
    if event.is_group:
        try:
            chat = await event.get_chat()
            target_in_group = await client.get_permissions(chat, target_user_id)
            if not target_in_group:
                await event.respond('❌ User not found in this group!')
                raise events.StopPropagation
        except Exception as e:
            await event.respond('❌ User not found in this group!')
            raise events.StopPropagation
    
    if not target_user:
        await event.respond('❌ User not found in bot database!')
        raise events.StopPropagation
    
    if target_user.get('banned'):
        await event.respond('❌ This user is already banned!')
    else:
        ban_user(target_user['user_id'])
        group_name = ""
        if event.is_group:
            chat = await event.get_chat()
            group_name = f" in {chat.title}"
        
        result_text = f"✅ User Banned{group_name}!\n\nUser ID: {target_user['user_id']}\nUsername: @{target_user['username']}\nName: {target_user['first_name']}"
        await event.respond(result_text)
        try:
            await client.send_message(target_user['user_id'], f'🚫 You have been BANNED{group_name}.')
        except Exception:
            pass
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r'/unban(?:\s+(.+))?'))
async def unban_handler(event):
    sender = await event.get_sender()
    if not sender:
        raise events.StopPropagation
    
    # Check admin permission
    has_permission = await check_admin_permission(event, sender.id)
    if not has_permission:
        await event.respond('🔐 Only bot owner or group admins can use this command!')
        raise events.StopPropagation
    
    # Get target user
    target_user_id = None
    target_user = None
    match = event.pattern_match
    
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.from_id:
            target_user_id = reply_msg.from_id.user_id
            target_user = get_user(target_user_id)
    elif match.group(1):
        user_input = match.group(1).strip()
        if user_input.isdigit():
            target_user_id = int(user_input)
            target_user = get_user(target_user_id)
        elif user_input.startswith('@'):
            username = user_input[1:]
            all_users = get_all_users()
            for uid_str, user in all_users.items():
                if user.get('username') == username:
                    target_user = user
                    target_user_id = user['user_id']
                    break
        else:
            await event.respond('❌ Invalid format. Use: `/unban <user_id>` or `/unban @username` or reply with `/unban`')
            raise events.StopPropagation
    else:
        await event.respond('❌ No user specified. Use: `/unban <user_id>` or `/unban @username` or reply with `/unban`')
        raise events.StopPropagation
    
    # In group, verify target user is in the same group
    if event.is_group:
        try:
            chat = await event.get_chat()
            target_in_group = await client.get_permissions(chat, target_user_id)
            if not target_in_group:
                await event.respond('❌ User not found in this group!')
                raise events.StopPropagation
        except Exception as e:
            await event.respond('❌ User not found in this group!')
            raise events.StopPropagation
    
    if not target_user:
        await event.respond('❌ User not found in bot database!')
        raise events.StopPropagation
    
    if not target_user.get('banned'):
        await event.respond('❌ This user is not banned!')
    else:
        unban_user(target_user['user_id'])
        group_name = ""
        if event.is_group:
            chat = await event.get_chat()
            group_name = f" in {chat.title}"
        
        result_text = f"✅ User Unbanned{group_name}!\n\nUser ID: {target_user['user_id']}\nUsername: @{target_user['username']}\nName: {target_user['first_name']}"
        await event.respond(result_text)
        try:
            await client.send_message(target_user['user_id'], f'✅ You have been UNBANNED{group_name}!')
        except Exception:
            pass
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r'/info(?:\s+(.+))?'))
async def info_handler(event):
    sender = await event.get_sender()
    if not sender:
        raise events.StopPropagation
    
    # Check admin permission
    has_permission = await check_admin_permission(event, sender.id)
    if not has_permission:
        await event.respond('🔐 Only bot owner or group admins can use this command!')
        raise events.StopPropagation
    
    # Get target user
    target_user_id = None
    target_user = None
    match = event.pattern_match
    
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.from_id:
            target_user_id = reply_msg.from_id.user_id
            target_user = get_user(target_user_id)
    elif match.group(1):
        user_input = match.group(1).strip()
        if user_input.isdigit():
            target_user_id = int(user_input)
            target_user = get_user(target_user_id)
        elif user_input.startswith('@'):
            username = user_input[1:]
            all_users = get_all_users()
            for uid_str, user in all_users.items():
                if user.get('username') == username:
                    target_user = user
                    target_user_id = user['user_id']
                    break
        else:
            await event.respond('❌ Invalid format. Use: `/info <user_id>` or `/info @username` or reply with `/info`')
            raise events.StopPropagation
    else:
        await event.respond('❌ No user specified. Use: `/info <user_id>` or `/info @username` or reply with `/info`')
        raise events.StopPropagation
    
    # In group, verify target user is in the same group
    if event.is_group:
        try:
            chat = await event.get_chat()
            target_in_group = await client.get_permissions(chat, target_user_id)
            if not target_in_group:
                await event.respond('❌ User not found in this group!')
                raise events.StopPropagation
        except Exception as e:
            await event.respond('❌ User not found in this group!')
            raise events.StopPropagation
    
    if not target_user:
        await event.respond('❌ User not found in bot database!')
        raise events.StopPropagation
    
    info_text = f"ℹ️ USER DETAILS\n\n"
    info_text += f"👤 ID: {target_user['user_id']}\n"
    info_text += f"👤 Username: @{target_user['username']}\n"
    info_text += f"📝 Name: {target_user['first_name']}\n"
    info_text += f"💬 Messages: {target_user['messages']}\n"
    info_text += f"📅 Joined: {target_user['joined'][:10]}\n"
    info_text += f"⏰ Full Join Date: {target_user['joined']}\n"
    info_text += f"🔄 Status: {'🚫 BANNED' if target_user['banned'] else '✅ ACTIVE'}\n"
    info_text += f"📊 User Status: {target_user['status']}\n"
    
    if event.is_group:
        chat = await event.get_chat()
        info_text += f"\n📍 Group: {chat.title}"
    
    await event.respond(info_text)
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/hello'))
async def hello_handler(event):
    sender = await event.get_sender()
    await event.respond(f'Hello {sender.first_name}!')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/time'))
async def time_handler(event):
    current_time = datetime.now().strftime("%H:%M:%S")
    await event.respond(f'Current time: {current_time}')
    raise events.StopPropagation

print("Bot started!")
client.run_until_disconnected()
