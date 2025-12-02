from telethon.tl.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_owner_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text='🛠️ Tools', callback_data=b'owner_tools')],
        [
            InlineKeyboardButton(text='👥 Users', callback_data=b'owner_users'),
            InlineKeyboardButton(text='📢 Broadcast', callback_data=b'owner_broadcast')
        ],
        [
            InlineKeyboardButton(text='📊 Status', callback_data=b'owner_status'),
            InlineKeyboardButton(text='⚙️ Settings', callback_data=b'owner_settings')
        ],
    ]
    return InlineKeyboardMarkup(buttons)

def get_user_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text='🛠️ Tools', callback_data=b'user_tools')],
        [
            InlineKeyboardButton(text='👤 Profile', callback_data=b'user_profile'),
            InlineKeyboardButton(text='❓ Help', callback_data=b'user_help')
        ],
        [InlineKeyboardButton(text='ℹ️ About', callback_data=b'user_about')],
    ]
    return InlineKeyboardMarkup(buttons)

def get_users_detail_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text='🚫 Ban', callback_data=b'user_ban'),
            InlineKeyboardButton(text='✅ Unban', callback_data=b'user_unban')
        ],
        [InlineKeyboardButton(text='ℹ️ Info', callback_data=b'user_info')],
        [InlineKeyboardButton(text='⬅️ Back', callback_data=b'owner_users_back')],
    ]
    return InlineKeyboardMarkup(buttons)

def get_settings_keyboard():
    buttons = [
        [InlineKeyboardButton(text='🛠️ Tools', callback_data=b'owner_tools')],
        [
            InlineKeyboardButton(text='✍️ Start Text', callback_data=b'setting_start_text'),
            InlineKeyboardButton(text='🔄 Sudo-Force', callback_data=b'setting_sudo_force')
        ],
        [InlineKeyboardButton(text='👥 Handle Group', callback_data=b'setting_handle_group')],
        [InlineKeyboardButton(text='⬅️ Back', callback_data=b'settings_back')],
    ]
    return InlineKeyboardMarkup(buttons)

def get_back_keyboard():
    buttons = [[InlineKeyboardButton(text='⬅️ Back', callback_data=b'back_to_main')]]
    return InlineKeyboardMarkup(buttons)
