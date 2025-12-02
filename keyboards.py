from telethon.tl.custom import InlineBuilder

def get_owner_main_keyboard(client):
    buttons = InlineBuilder(client)
    buttons.row(buttons.button('🛠️ Tools', data=b'owner_tools'))
    buttons.row(
        buttons.button('👥 Users', data=b'owner_users'),
        buttons.button('📢 Broadcast', data=b'owner_broadcast')
    )
    buttons.row(
        buttons.button('📊 Status', data=b'owner_status'),
        buttons.button('⚙️ Settings', data=b'owner_settings')
    )
    return buttons.build()

def get_user_main_keyboard(client):
    buttons = InlineBuilder(client)
    buttons.row(buttons.button('🛠️ Tools', data=b'user_tools'))
    buttons.row(
        buttons.button('👤 Profile', data=b'user_profile'),
        buttons.button('❓ Help', data=b'user_help')
    )
    buttons.row(buttons.button('ℹ️ About', data=b'user_about'))
    return buttons.build()

def get_users_detail_keyboard(client):
    buttons = InlineBuilder(client)
    buttons.row(
        buttons.button('🚫 Ban', data=b'user_ban'),
        buttons.button('✅ Unban', data=b'user_unban')
    )
    buttons.row(buttons.button('ℹ️ Info', data=b'user_info'))
    buttons.row(buttons.button('⬅️ Back', data=b'owner_users_back'))
    return buttons.build()

def get_settings_keyboard(client):
    buttons = InlineBuilder(client)
    buttons.row(buttons.button('🛠️ Tools', data=b'owner_tools'))
    buttons.row(
        buttons.button('✍️ Start Text', data=b'setting_start_text'),
        buttons.button('🔄 Sudo-Force', data=b'setting_sudo_force')
    )
    buttons.row(buttons.button('👥 Handle Group', data=b'setting_handle_group'))
    buttons.row(buttons.button('⬅️ Back', data=b'settings_back'))
    return buttons.build()

def get_back_keyboard(client):
    buttons = InlineBuilder(client)
    buttons.row(buttons.button('⬅️ Back', data=b'back_to_main'))
    return buttons.build()
