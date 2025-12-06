
# 🤖 Telegram MultiBot

A powerful Telegram bot with multiple tools and features built using Telethon.

## 📋 Features

### 🛠️ Tools
- 📱 **Number Info** - Get information about mobile numbers
- 🆔 **Aadhar Info** - Fetch Aadhar details
- 👨‍👩‍👧‍👦 **Aadhar to Family** - Get family details from Aadhar
- 🚗 **Vehicle Info** - Vehicle registration lookup
- 🏦 **IFSC Info** - Bank IFSC code details
- 🇵🇰 **Pakistan Number** - Pakistan mobile number info
- 📍 **PIN Code Info** - Location details from PIN code
- 📱 **IMEI Info** - Device IMEI information
- 🌐 **IP Info** - IP address geolocation

### 👥 User Management
- Ban/Unban users
- User statistics tracking
- Message count monitoring
- User profile viewing

### 📢 Broadcast
- Send messages to all users
- Detailed broadcast reports
- Custom message formatting with placeholders

### 📺 Channel Management
- Sub-force (mandatory channel subscription)
- Add/Remove channels
- Channel verification

### 👥 Group Management
- Connect multiple groups
- Custom welcome messages
- Auto-delete welcome messages
- Ban/Unban in groups
- Admin permission checks

### ⚙️ Settings
- Customizable start text (owner & user)
- Welcome message customization
- Tool enable/disable
- Multiple API support per tool
- Database backup to channel

## 🚀 Setup

1. **Environment Variables**
   - `API_ID` - Your Telegram API ID
   - `API_HASH` - Your Telegram API Hash
   - `BOT_TOKEN` - Your Bot Token from @BotFather
   - `OWNER_ID` - Your Telegram User ID

2. **Install Dependencies**
   ```bash
   pip install telethon aiohttp
   ```

3. **Run Bot**
   ```bash
   python bot.py
   ```

## 📝 Commands

### Owner Commands
- `/start` - Main control panel
- `/ban <user_id/@username>` - Ban user
- `/unban <user_id/@username>` - Unban user
- `/info <user_id/@username>` - Get user info

### User Commands
- `/start` - Access bot features
- `/num <number>` - Number info lookup
- `/adhar <aadhar>` - Aadhar info lookup
- `/family <aadhar>` - Family details lookup
- `/vhe <vehicle>` - Vehicle info lookup
- `/ifsc <code>` - IFSC code lookup
- `/pak <number>` - Pakistan number lookup
- `/pin <pincode>` - PIN code info lookup
- `/imei <imei>` - IMEI info lookup
- `/ip <ip>` - IP address info lookup
- `/hello` - Simple greeting
- `/time` - Get current time

### Group Commands
- `/ban` - Ban user (admin only)
- `/unban` - Unban user (admin only)
- `/info` - Get user info (admin only)

## 🎨 Customization

### Text Placeholders
You can use these placeholders in custom start text and broadcast messages:
- `{greeting}` - Time-based greeting
- `{first_name}` - User's first name
- `{username}` - User's username
- `{user_id}` - User's ID
- `{total_users}` - Total users count
- `{active_users}` - Active users count
- `{date}` - Current date
- `{time}` - Current time
- `{datetime}` - Full datetime
- `{bot_name}` - Bot name
- `{user_messages}` - User's message count
- `{joined_date}` - User's join date

### API Configuration
Each tool supports multiple APIs with automatic failover. If one API fails, the bot automatically tries the next available API.

## 💾 Database

The bot uses SQLite database (`bot_database.db`) to store:
- User data
- Channel configurations
- Group settings
- Tool settings
- API configurations
- Custom texts

### Backup
Automatic database backup to configured Telegram channel with customizable interval.

## 🔒 Security Features
- Sub-force (mandatory channel subscription)
- User ban system
- Admin-only commands in groups
- Anonymous admin support
- Owner-only features

## 📊 Statistics
- Total users count
- Active/Banned users
- Total messages
- Active tools count
- Connected channels & groups

## 🛡️ Error Handling
- Comprehensive error logging
- API failover mechanism
- Database connection pooling
- Graceful shutdown

## 📄 License
This project is open source and available for personal use.

## 👨‍💻 Developer
Built with ❤️ using Telethon

---

**Note:** Keep your API credentials secure and never share them publicly.
