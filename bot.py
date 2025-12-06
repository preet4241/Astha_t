# -*- coding: utf-8 -*-
from telethon import TelegramClient, events, Button
import os
import random
import asyncio
from datetime import datetime, timedelta
from database import (
    add_user, get_user, ban_user, unban_user, 
    get_all_users, get_stats, increment_messages,
    set_setting, get_setting, add_channel, remove_channel,
    get_all_channels, channel_exists, add_group, remove_group,
    get_all_groups, group_exists, is_group_active,
    set_tool_status, get_tool_status, get_all_active_tools
)

api_id = int(os.getenv('API_ID', '22880380'))
api_hash = os.getenv('API_HASH', '08dae0d98b2dc8f8dc4e6a9ff97a071b')
bot_token = os.getenv('BOT_TOKEN', '8028312869:AAErsD7WmHHw11c2lL2Jdoj_DBU4bqRv_kQ')
owner_id = int(os.getenv('OWNER_ID', '8267410570'))

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

broadcast_temp = {}
broadcast_stats = {}
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
    """Get a random welcome message - includes both default and custom messages"""
    messages = get_default_welcome_messages()
    
    # Get custom welcome messages from database
    custom_msg = get_setting('group_welcome_text', '')
    if custom_msg:
        # Add custom message to the pool
        messages.append(custom_msg)
    
    # Pick random message from combined pool
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
    # Check if in group and group is removed
    if event.is_group:
        chat = await event.get_chat()
        if not is_group_active(chat.id):
            print(f"[LOG] ⏭️ /start ignored - Group {chat.title} is removed")
            raise events.StopPropagation
    
    sender = await event.get_sender()
    if not sender:
        print(f"[LOG] ⚠️ /start received but no sender info")
        return
    
    print(f"[LOG] 🚀 /start command from {sender.first_name} (@{sender.username or 'no_username'}) ID: {sender.id}")
    add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
    
    user_data = get_user(sender.id)
    if user_data and user_data.get('banned'):
        print(f"[LOG] 🚫 Banned user {sender.id} tried to use /start")
        await event.respond('🚫 You are BANNED from using this bot!')
        raise events.StopPropagation
    
    stats = get_stats()
    
    if sender.id == owner_id:
        print(f"[LOG] 👑 Owner {sender.id} accessed bot")
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
            try:
                await event.edit('REMOVE GROUP\n\nSelect group to remove:', buttons=buttons)
            except:
                await event.answer('✅ Group removed!')
    
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
            try:
                await event.edit('REMOVE GROUP\n\nSelect group to remove:', buttons=buttons)
            except:
                await event.answer('✅ Group removed!')
    
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
            [Button.inline('🛠️ Tools Handler', b'setting_tools_handler')],
            [Button.inline('📺 Sub-Force', b'setting_sub_force'), Button.inline('👥 Groups', b'setting_groups')],
            [Button.inline('📝 Start Text', b'setting_start_text'), Button.inline('💾 Backup', b'setting_backup')],
            [Button.inline('🔙 Back', b'owner_back')],
        ]
        settings_text = "BOT SETTINGS\n\nConfigure your bot:"
        await event.edit(settings_text, buttons=buttons)
    
    elif data == b'setting_backup':
        await event.edit('💾 BACKUP\n\nBot backup feature coming soon...', buttons=[[Button.inline('🔙 Back', b'owner_settings')]])
    
    elif data == b'setting_tools_handler':
        active_tools = get_all_active_tools()
        buttons = []
        
        tools_map = [
            ('number_info', '📱 Number Info', b'tool_number_info'),
            ('aadhar_info', '🆔 Aadhar Info', b'tool_aadhar_info'),
            ('aadhar_family', '👨‍👩‍👧‍👦 Aadhar to Family', b'tool_aadhar_family'),
            ('vehicle_info', '🚗 Vehicle Info', b'tool_vehicle_info'),
            ('ifsc_info', '🏦 IFSC Info', b'tool_ifsc_info'),
            ('pak_num', '🇵🇰 Pak Num Info', b'tool_pak_num'),
            ('pincode_info', '📍 Pin Code Info', b'tool_pincode_info'),
            ('imei_info', '📱 IMEI Info', b'tool_imei_info'),
            ('ip_info', '🌐 IP Info', b'tool_ip_info'),
        ]
        
        row = []
        for idx, (tool_key, tool_name, callback) in enumerate(tools_map):
            if get_tool_status(tool_key):
                row.append(Button.inline(tool_name, callback))
                if len(row) == 2 or idx == len(tools_map) - 1:
                    buttons.append(row)
                    row = []
        
        buttons.append([Button.inline('🔙 Back', b'owner_settings')])
        
        tools_text = "🛠️ TOOLS HANDLER\n\nActive Tools:"
        await event.edit(tools_text, buttons=buttons)
    
    elif data == b'tool_number_info':
        status = get_tool_status('number_info')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_number_add_api'), Button.inline('➖ Remove API', b'tool_number_remove_api')],
            [Button.inline('📋 All API', b'tool_number_all_api'), Button.inline('📊 Status', b'tool_number_status')],
            [Button.inline(f'{status_text}', b'tool_number_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('📱 NUMBER INFO\n\nManage Number Info APIs', buttons=buttons)
    
    elif data == b'tool_number_toggle':
        current_status = get_tool_status('number_info')
        set_tool_status('number_info', not current_status)
        new_status = get_tool_status('number_info')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_number_add_api'), Button.inline('➖ Remove API', b'tool_number_remove_api')],
            [Button.inline('📋 All API', b'tool_number_all_api'), Button.inline('📊 Status', b'tool_number_status')],
            [Button.inline(f'{status_text}', b'tool_number_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('📱 NUMBER INFO\n\nManage Number Info APIs', buttons=buttons)
    
    elif data == b'tool_aadhar_info':
        status = get_tool_status('aadhar_info')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_aadhar_add_api'), Button.inline('➖ Remove API', b'tool_aadhar_remove_api')],
            [Button.inline('📋 All API', b'tool_aadhar_all_api'), Button.inline('📊 Status', b'tool_aadhar_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_aadhar_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🆔 AADHAR INFO\n\nManage Aadhar Info APIs', buttons=buttons)
    
    elif data == b'tool_aadhar_toggle':
        current_status = get_tool_status('aadhar_info')
        set_tool_status('aadhar_info', not current_status)
        new_status = get_tool_status('aadhar_info')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_aadhar_add_api'), Button.inline('➖ Remove API', b'tool_aadhar_remove_api')],
            [Button.inline('📋 All API', b'tool_aadhar_all_api'), Button.inline('📊 Status', b'tool_aadhar_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_aadhar_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🆔 AADHAR INFO\n\nManage Aadhar Info APIs', buttons=buttons)
    
    elif data == b'tool_aadhar_family':
        status = get_tool_status('aadhar_family')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_family_add_api'), Button.inline('➖ Remove API', b'tool_family_remove_api')],
            [Button.inline('📋 All API', b'tool_family_all_api'), Button.inline('📊 Status', b'tool_family_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_family_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('👨‍👩‍👧‍👦 AADHAR TO FAMILY\n\nManage Aadhar to Family APIs', buttons=buttons)
    
    elif data == b'tool_family_toggle':
        current_status = get_tool_status('aadhar_family')
        set_tool_status('aadhar_family', not current_status)
        new_status = get_tool_status('aadhar_family')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_family_add_api'), Button.inline('➖ Remove API', b'tool_family_remove_api')],
            [Button.inline('📋 All API', b'tool_family_all_api'), Button.inline('📊 Status', b'tool_family_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_family_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('👨‍👩‍👧‍👦 AADHAR TO FAMILY\n\nManage Aadhar to Family APIs', buttons=buttons)
    
    elif data == b'tool_vehicle_info':
        status = get_tool_status('vehicle_info')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_vehicle_add_api'), Button.inline('➖ Remove API', b'tool_vehicle_remove_api')],
            [Button.inline('📋 All API', b'tool_vehicle_all_api'), Button.inline('📊 Status', b'tool_vehicle_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_vehicle_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🚗 VEHICLE INFO\n\nManage Vehicle Info APIs', buttons=buttons)
    
    elif data == b'tool_vehicle_toggle':
        current_status = get_tool_status('vehicle_info')
        set_tool_status('vehicle_info', not current_status)
        new_status = get_tool_status('vehicle_info')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_vehicle_add_api'), Button.inline('➖ Remove API', b'tool_vehicle_remove_api')],
            [Button.inline('📋 All API', b'tool_vehicle_all_api'), Button.inline('📊 Status', b'tool_vehicle_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_vehicle_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🚗 VEHICLE INFO\n\nManage Vehicle Info APIs', buttons=buttons)
    
    elif data == b'tool_ifsc_info':
        status = get_tool_status('ifsc_info')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_ifsc_add_api'), Button.inline('➖ Remove API', b'tool_ifsc_remove_api')],
            [Button.inline('📋 All API', b'tool_ifsc_all_api'), Button.inline('📊 Status', b'tool_ifsc_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_ifsc_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🏦 IFSC INFO\n\nManage IFSC Info APIs', buttons=buttons)
    
    elif data == b'tool_ifsc_toggle':
        current_status = get_tool_status('ifsc_info')
        set_tool_status('ifsc_info', not current_status)
        new_status = get_tool_status('ifsc_info')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_ifsc_add_api'), Button.inline('➖ Remove API', b'tool_ifsc_remove_api')],
            [Button.inline('📋 All API', b'tool_ifsc_all_api'), Button.inline('📊 Status', b'tool_ifsc_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_ifsc_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🏦 IFSC INFO\n\nManage IFSC Info APIs', buttons=buttons)
    
    elif data == b'tool_pak_num':
        status = get_tool_status('pak_num')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_pak_add_api'), Button.inline('➖ Remove API', b'tool_pak_remove_api')],
            [Button.inline('📋 All API', b'tool_pak_all_api'), Button.inline('📊 Status', b'tool_pak_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_pak_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🇵🇰 PAK NUM INFO\n\nManage Pak Number APIs', buttons=buttons)
    
    elif data == b'tool_pak_toggle':
        current_status = get_tool_status('pak_num')
        set_tool_status('pak_num', not current_status)
        new_status = get_tool_status('pak_num')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_pak_add_api'), Button.inline('➖ Remove API', b'tool_pak_remove_api')],
            [Button.inline('📋 All API', b'tool_pak_all_api'), Button.inline('📊 Status', b'tool_pak_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_pak_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🇵🇰 PAK NUM INFO\n\nManage Pak Number APIs', buttons=buttons)
    
    elif data == b'tool_pincode_info':
        status = get_tool_status('pincode_info')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_pin_add_api'), Button.inline('➖ Remove API', b'tool_pin_remove_api')],
            [Button.inline('📋 All API', b'tool_pin_all_api'), Button.inline('📊 Status', b'tool_pin_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_pin_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('📍 PIN CODE INFO\n\nManage Pin Code APIs', buttons=buttons)
    
    elif data == b'tool_pin_toggle':
        current_status = get_tool_status('pincode_info')
        set_tool_status('pincode_info', not current_status)
        new_status = get_tool_status('pincode_info')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_pin_add_api'), Button.inline('➖ Remove API', b'tool_pin_remove_api')],
            [Button.inline('📋 All API', b'tool_pin_all_api'), Button.inline('📊 Status', b'tool_pin_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_pin_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('📍 PIN CODE INFO\n\nManage Pin Code APIs', buttons=buttons)
    
    elif data == b'tool_imei_info':
        status = get_tool_status('imei_info')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_imei_add_api'), Button.inline('➖ Remove API', b'tool_imei_remove_api')],
            [Button.inline('📋 All API', b'tool_imei_all_api'), Button.inline('📊 Status', b'tool_imei_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_imei_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('📱 IMEI INFO\n\nManage IMEI Info APIs', buttons=buttons)
    
    elif data == b'tool_imei_toggle':
        current_status = get_tool_status('imei_info')
        set_tool_status('imei_info', not current_status)
        new_status = get_tool_status('imei_info')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_imei_add_api'), Button.inline('➖ Remove API', b'tool_imei_remove_api')],
            [Button.inline('📋 All API', b'tool_imei_all_api'), Button.inline('📊 Status', b'tool_imei_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_imei_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('📱 IMEI INFO\n\nManage IMEI Info APIs', buttons=buttons)
    
    elif data == b'tool_ip_info':
        status = get_tool_status('ip_info')
        status_text = '✅ Active' if status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_ip_add_api'), Button.inline('➖ Remove API', b'tool_ip_remove_api')],
            [Button.inline('📋 All API', b'tool_ip_all_api'), Button.inline('📊 Status', b'tool_ip_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_ip_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🌐 IP INFO\n\nManage IP Info APIs', buttons=buttons)
    
    elif data == b'tool_ip_toggle':
        current_status = get_tool_status('ip_info')
        set_tool_status('ip_info', not current_status)
        new_status = get_tool_status('ip_info')
        status_text = '✅ Active' if new_status else '❌ Inactive'
        buttons = [
            [Button.inline('➕ Add API', b'tool_ip_add_api'), Button.inline('➖ Remove API', b'tool_ip_remove_api')],
            [Button.inline('📋 All API', b'tool_ip_all_api'), Button.inline('📊 Status', b'tool_ip_status')],
            [Button.inline(f'🔄 {status_text}', b'tool_ip_toggle')],
            [Button.inline('🔙 Back', b'setting_tools_handler')],
        ]
        await event.edit('🌐 IP INFO\n\nManage IP Info APIs', buttons=buttons)
    
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
        broadcast_temp[sender.id] = True
        buttons = [[Button.inline('❌ Cancel', b'owner_back')]]
        help_text = "📝 Type your broadcast message:\n\nAvailable Placeholders:\n{greeting} - Good Morning/Afternoon/Evening/Night\n{first_name} - User's first name\n{username} - User's username\n{user_id} - User's ID\n{total_users} - Total users count\n{active_users} - Active users count\n{date} - Today's date (DD-MM-YYYY)\n{time} - Current time (HH:MM:SS)\n{datetime} - Full date and time\n{bot_name} - Bot name"
        await event.edit(help_text, buttons=buttons)
    
    elif data == b'owner_status':
        stats = get_stats()
        current_time = datetime.now().strftime("%H:%M:%S")
        status_text = f"📊 BOT STATUS\n\nUsers: {stats['total_users']}\nActive: {stats['active_users']}\nMessages: {stats['total_messages']}\nTime: {current_time}"
        buttons = [[Button.inline('🔙 Back', b'owner_back')]]
        await event.edit(status_text, buttons=buttons)
    
    elif data == b'owner_tools':
        buttons = []
        tools_map = [
            ('number_info', '📱 Number Info', b'tool_number_info'),
            ('aadhar_info', '🆔 Aadhar Info', b'tool_aadhar_info'),
            ('aadhar_family', '👨‍👩‍👧‍👦 Aadhar to Family', b'tool_aadhar_family'),
            ('vehicle_info', '🚗 Vehicle Info', b'tool_vehicle_info'),
            ('ifsc_info', '🏦 IFSC Info', b'tool_ifsc_info'),
            ('pak_num', '🇵🇰 Pak Num Info', b'tool_pak_num'),
            ('pincode_info', '📍 Pin Code Info', b'tool_pincode_info'),
            ('imei_info', '📱 IMEI Info', b'tool_imei_info'),
            ('ip_info', '🌐 IP Info', b'tool_ip_info'),
        ]
        
        row = []
        for idx, (tool_key, tool_name, callback) in enumerate(tools_map):
            if get_tool_status(tool_key):
                row.append(Button.inline(tool_name, callback))
                if len(row) == 2 or idx == len(tools_map) - 1:
                    buttons.append(row)
                    row = []
        
        buttons.append([Button.inline('🔙 Back', b'owner_back')])
        await event.edit('🛠️ TOOLS\n\nSelect an active tool to use:', buttons=buttons)
    
    elif data == b'user_tools':
        buttons = []
        tools_map = [
            ('number_info', '📱 Number Info', b'tool_number_info'),
            ('aadhar_info', '🆔 Aadhar Info', b'tool_aadhar_info'),
            ('aadhar_family', '👨‍👩‍👧‍👦 Aadhar to Family', b'tool_aadhar_family'),
            ('vehicle_info', '🚗 Vehicle Info', b'tool_vehicle_info'),
            ('ifsc_info', '🏦 IFSC Info', b'tool_ifsc_info'),
            ('pak_num', '🇵🇰 Pak Num Info', b'tool_pak_num'),
            ('pincode_info', '📍 Pin Code Info', b'tool_pincode_info'),
            ('imei_info', '📱 IMEI Info', b'tool_imei_info'),
            ('ip_info', '🌐 IP Info', b'tool_ip_info'),
        ]
        
        row = []
        for idx, (tool_key, tool_name, callback) in enumerate(tools_map):
            if get_tool_status(tool_key):
                row.append(Button.inline(tool_name, callback))
                if len(row) == 2 or idx == len(tools_map) - 1:
                    buttons.append(row)
                    row = []
        
        buttons.append([Button.inline('🔙 Back', b'user_back')])
        await event.edit('🛠️ TOOLS\n\nSelect an active tool to use:', buttons=buttons)
    
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
    
    elif data == b'broadcast_detail':
        stats = broadcast_stats.get(sender.id)
        if stats:
            # Create the detail text file content
            file_content = "📋 BROADCAST REPORT\n"
            file_content += f"{'='*50}\n\n"
            file_content += f"✅ SUCCESSFULLY SENT: {stats['sent_count']}\n"
            file_content += f"{'-'*50}\n"
            
            if stats['sent']:
                for user_info in stats['sent']:
                    file_content += f"{user_info}\n"
            else:
                file_content += "No users\n"
            
            file_content += f"\n\n❌ FAILED TO SEND: {stats['failed_count']}\n"
            file_content += f"{'-'*50}\n"
            
            if stats['failed']:
                for user_info in stats['failed']:
                    file_content += f"{user_info}\n"
            else:
                file_content += "No failures\n"
            
            file_content += f"\n\n{'='*50}\n"
            file_content += f"Total Users: {stats['sent_count'] + stats['failed_count']}\n"
            
            # Write to file
            filename = f"broadcast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # Send file
            try:
                await client.send_file(sender.id, filename)
                await event.answer("📄 Report sent!", alert=False)
            except Exception as e:
                await event.answer(f"Error sending file: {str(e)}", alert=True)
                print(f"[LOG] ❌ Error sending broadcast report: {e}")

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
        
        print(f"[LOG] 📢 Starting broadcast to {len(all_users)} users")
        sent_count = 0
        failed_count = 0
        sent_users = []
        failed_users = []
        
        for user_id_str, user in all_users.items():
            if user.get('banned'):
                continue
            
            try:
                # Create a temporary user object for formatting
                class UserObj:
                    def __init__(self, user_data):
                        self.first_name = user_data.get('first_name', 'User')
                        self.username = user_data.get('username', 'user')
                        self.id = user_data.get('user_id', 0)
                
                user_obj = UserObj(user)
                # Format message with placeholders for each user
                formatted_message = format_text(message, user_obj, stats, user)
                await client.send_message(int(user_id_str), formatted_message)
                sent_count += 1
                sent_users.append(f"ID: {user['user_id']} | @{user['username']} | {user['first_name']}")
            except Exception as e:
                failed_count += 1
                failed_users.append(f"ID: {user['user_id']} | @{user['username']} | {user['first_name']} | Error: {str(e)}")
                print(f"[LOG] ❌ Broadcast failed to user {user_id_str}: {e}")
        
        # Store stats for detail view
        broadcast_stats[sender.id] = {
            'sent': sent_users,
            'failed': failed_users,
            'sent_count': sent_count,
            'failed_count': failed_count
        }
        
        print(f"[LOG] ✅ Broadcast complete: {sent_count} sent, {failed_count} failed")
        broadcast_temp[sender.id] = False
        result_text = f"✅ Broadcast Complete!\n\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}"
        buttons = [
            [Button.inline('📋 Detail', b'broadcast_detail'), Button.inline('🔙 Back', b'owner_back')]
        ]
        await event.respond(result_text, buttons=buttons)
        raise events.StopPropagation

# Track processed join events to avoid duplicates
processed_joins = {}

@client.on(events.ChatAction)
async def member_joined_handler(event):
    """Handle new members joining the group"""
    try:
        # Only process if there's an action message (user joined/added)
        if not event.action_message:
            return
            
        if event.user_joined or event.user_added:
            chat = await event.get_chat()
            if not chat:
                print(f"[LOG] ⚠️ Could not get chat info in member_joined_handler")
                return
            
            grp_id = chat.id
            grp_name = chat.username or str(chat.id)
            grp_title = chat.title or 'Unknown Group'
            
            # Check if group is in database (if removed, don't send welcome)
            if not group_exists(grp_id):
                print(f"[LOG] ⏭️ Group {grp_title} not in database, skipping welcome message")
                return
            
            # Get the user who joined
            user = await event.get_user()
            if not user:
                print(f"[LOG] ⚠️ Could not get user info for join event in {grp_title}")
                return
            
            # Create unique key based on message ID to prevent duplicate processing
            if hasattr(event.action_message, 'id'):
                join_key = f"{grp_id}_{user.id}_{event.action_message.id}"
            else:
                join_key = f"{grp_id}_{user.id}_{int(datetime.now().timestamp())}"
            
            # Check if we already processed this exact join event
            if join_key in processed_joins:
                print(f"[LOG] ⏭️ Skipping duplicate join event for {user.first_name} in {grp_title}")
                return
            
            # Mark as processed
            processed_joins[join_key] = datetime.now().timestamp()
            
            print(f"[LOG] 👤 New member joined: {user.first_name} (@{user.username or 'no_username'}) ID: {user.id}")
            print(f"[LOG] 📍 Group: {grp_title} (ID: {grp_id})")
            
            # Add group to database if not exists
            if not group_exists(grp_id):
                add_group(grp_id, grp_name, grp_title)
                print(f"[LOG] ✅ Group '{grp_title}' added to database")
            
            # Add user to database
            add_user(user.id, user.username or 'unknown', user.first_name or 'User')
            print(f"[LOG] ✅ User '{user.first_name}' added/updated in database")
            
            # Get random welcome message (includes both default and custom messages)
            user_username = user.username or user.first_name or "user"
            msg_text = get_random_welcome_message(user_username, grp_title)
            print(f"[LOG] 🎲 Random welcome message selected: {msg_text[:50]}...")
            
            try:
                # Send welcome message
                welcome_message = await client.send_message(chat, msg_text)
                print(f"[LOG] ✅ Welcome message sent to {user.first_name} in {grp_title}")
                
                # Schedule deletion after 15 seconds
                async def delete_after_delay():
                    await asyncio.sleep(15)
                    try:
                        await welcome_message.delete()
                        print(f"[LOG] 🗑️ Welcome message auto-deleted for {user.first_name} in {grp_title}")
                    except Exception as del_err:
                        print(f"[LOG] ❌ Could not delete welcome message: {del_err}")
                
                # Run deletion in background
                asyncio.create_task(delete_after_delay())
            except Exception as send_err:
                print(f"[LOG] ❌ Error sending welcome message: {send_err}")
                
    except Exception as e:
        print(f"[LOG] ❌ Error in member_joined_handler: {e}")

@client.on(events.NewMessage(incoming=True))
async def group_message_handler(event):
    try:
        if event.is_group:
            chat = await event.get_chat()
            grp_id = chat.id
            
            # Ignore messages from removed groups
            if not is_group_active(grp_id):
                return
            
            sender = await event.get_sender()
            
            if not sender or not chat:
                return
            grp_name = chat.username or str(chat.id)
            grp_title = chat.title or 'Unknown'
            
            # Only track messages if group is in database
            if group_exists(grp_id):
                # Track messages
                add_user(sender.id, sender.username or 'unknown', sender.first_name or 'User')
                increment_messages(sender.id)
            else:
                print(f"[LOG] ⏭️ Group '{grp_title}' not in database, skipping message tracking")
    except Exception as e:
        print(f"[LOG] ❌ Error in group_message_handler: {e}")

async def check_admin_permission(event, sender_id=None):
    """Check if user has admin permission (bot owner, group owner, or group admin or anonymous admin)"""
    from telethon.tl.types import PeerChannel, PeerUser
    
    # Bot owner has permission everywhere
    if sender_id and sender_id == owner_id:
        return True
    
    # In private chat, only bot owner allowed
    if event.is_private:
        return sender_id == owner_id
    
    # In group, check if user is group owner or admin or anonymous admin
    if event.is_group:
        try:
            chat = await event.get_chat()
            
            # First check: is this an anonymous admin?
            # Anonymous posts have from_id as PeerChannel (the channel used for anonymous posting)
            if hasattr(event, 'from_id') and isinstance(event.from_id, PeerChannel):
                # This is an anonymous admin, return True
                print(f"Anonymous admin detected in group {chat.title}")
                return True
            
            # Second check: is this from the message's from_id as PeerChannel?
            if event.message and hasattr(event.message, 'from_id'):
                if isinstance(event.message.from_id, PeerChannel):
                    print(f"Anonymous admin detected via message.from_id in group {chat.title}")
                    return True
            
            # Third check: regular user with sender_id
            if sender_id:
                try:
                    participant = await client.get_permissions(chat, sender_id)
                    if participant.is_creator or participant.is_admin:
                        print(f"User {sender_id} is admin/creator in {chat.title}")
                        return True
                except Exception as perm_err:
                    print(f"Permission check failed for {sender_id}: {perm_err}")
                    pass
                    
        except Exception as e:
            print(f"Error in check_admin_permission: {e}")
            pass
    
    return False

@client.on(events.NewMessage(pattern=r'/ban(?:\s+(.+))?'))
async def ban_handler(event):
    # Ignore commands from removed groups
    if event.is_group:
        chat = await event.get_chat()
        if not is_group_active(chat.id):
            raise events.StopPropagation
    
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    
    # Check admin permission (allows anonymous admins too)
    has_permission = await check_admin_permission(event, sender_id)
    if not has_permission:
        await event.respond('🔐 Permission Denied! Only bot owner or group admins can use this!')
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
        # Ban user in bot database
        ban_user(target_user['user_id'])
        
        # If in group, also kick from group
        if event.is_group:
            try:
                chat = await event.get_chat()
                await client.edit_permissions(chat, target_user_id, view_messages=False)
                group_name = f" in {chat.title}"
            except Exception as kick_err:
                print(f"Could not kick user from group: {kick_err}")
                group_name = " in bot"
        else:
            group_name = " in bot"
        
        result_text = f"✅ User Banned{group_name}!\n\nUser ID: {target_user['user_id']}\nUsername: @{target_user['username']}\nName: {target_user['first_name']}"
        await event.respond(result_text)
        try:
            await client.send_message(target_user['user_id'], f'🚫 You have been BANNED{group_name}.')
        except Exception:
            pass
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r'/unban(?:\s+(.+))?'))
async def unban_handler(event):
    # Ignore commands from removed groups
    if event.is_group:
        chat = await event.get_chat()
        if not is_group_active(chat.id):
            raise events.StopPropagation
    
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    
    # Check admin permission (allows anonymous admins too)
    has_permission = await check_admin_permission(event, sender_id)
    if not has_permission:
        await event.respond('🔐 Permission Denied! Only bot owner or group admins can use this!')
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
        # Unban user in bot database
        unban_user(target_user['user_id'])
        
        # If in group, also restore permissions
        if event.is_group:
            try:
                from telethon.tl.types import ChatBannedRights
                chat = await event.get_chat()
                # Restore full permissions (no restrictions)
                await client.edit_permissions(chat, target_user_id, ChatBannedRights(until_date=None))
                group_name = f" in {chat.title}"
            except Exception as restore_err:
                print(f"Could not restore user in group: {restore_err}")
                group_name = " in bot"
        else:
            group_name = " in bot"
        
        result_text = f"✅ User Unbanned{group_name}!\n\nUser ID: {target_user['user_id']}\nUsername: @{target_user['username']}\nName: {target_user['first_name']}"
        await event.respond(result_text)
        try:
            await client.send_message(target_user['user_id'], f'✅ You have been UNBANNED{group_name}!')
        except Exception:
            pass
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern=r'/info(?:\s+(.+))?'))
async def info_handler(event):
    # Ignore commands from removed groups
    if event.is_group:
        chat = await event.get_chat()
        if not is_group_active(chat.id):
            raise events.StopPropagation
    
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    
    # Check admin permission (allows anonymous admins too)
    has_permission = await check_admin_permission(event, sender_id)
    if not has_permission:
        await event.respond('🔐 Permission Denied! Only bot owner or group admins can use this!')
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
    # Check if in removed group
    if event.is_group:
        chat = await event.get_chat()
        if not is_group_active(chat.id):
            raise events.StopPropagation
    
    sender = await event.get_sender()
    await event.respond(f'Hello {sender.first_name}!')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/time'))
async def time_handler(event):
    # Check if in removed group
    if event.is_group:
        chat = await event.get_chat()
        if not is_group_active(chat.id):
            raise events.StopPropagation
    
    current_time = datetime.now().strftime("%H:%M:%S")
    await event.respond(f'Current time: {current_time}')
    raise events.StopPropagation

print("Bot started!")
client.run_until_disconnected()
