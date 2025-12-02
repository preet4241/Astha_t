from telethon.tl.types import KeyboardButtonRow, KeyboardButton, ReplyKeyboardMarkup
from telethon.tl.types import InlineKeyboardButton, InlineKeyboardMarkupClass

owner_main_keyboard = [
    [
        InlineKeyboardButton(text='🛠️ Tools', callback_data=b'owner_tools'),
    ],
    [
        InlineKeyboardButton(text='👥 Users', callback_data=b'owner_users'),
        InlineKeyboardButton(text='📢 Broadcast', callback_data=b'owner_broadcast'),
    ],
    [
        InlineKeyboardButton(text='📊 Status', callback_data=b'owner_status'),
        InlineKeyboardButton(text='⚙️ Settings', callback_data=b'owner_settings'),
    ],
]

user_main_keyboard = [
    [
        InlineKeyboardButton(text='🛠️ Tools', callback_data=b'user_tools'),
    ],
    [
        InlineKeyboardButton(text='👤 Profile', callback_data=b'user_profile'),
        InlineKeyboardButton(text='❓ Help', callback_data=b'user_help'),
    ],
    [
        InlineKeyboardButton(text='ℹ️ About', callback_data=b'user_about'),
    ],
]

users_detail_keyboard = [
    [
        InlineKeyboardButton(text='🚫 Ban', callback_data=b'user_ban'),
        InlineKeyboardButton(text='✅ Unban', callback_data=b'user_unban'),
    ],
    [
        InlineKeyboardButton(text='ℹ️ Info', callback_data=b'user_info'),
    ],
    [
        InlineKeyboardButton(text='⬅️ Back', callback_data=b'owner_users_back'),
    ],
]

settings_keyboard = [
    [
        InlineKeyboardButton(text='🛠️ Tools', callback_data=b'owner_tools'),
    ],
    [
        InlineKeyboardButton(text='✍️ Start Text', callback_data=b'setting_start_text'),
        InlineKeyboardButton(text='🔄 Sudo-Force', callback_data=b'setting_sudo_force'),
    ],
    [
        InlineKeyboardButton(text='👥 Handle Group', callback_data=b'setting_handle_group'),
    ],
    [
        InlineKeyboardButton(text='⬅️ Back', callback_data=b'settings_back'),
    ],
]

back_keyboard = [
    [
        InlineKeyboardButton(text='⬅️ Back', callback_data=b'back_to_main'),
    ],
]
