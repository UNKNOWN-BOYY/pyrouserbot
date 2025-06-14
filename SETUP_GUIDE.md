# Environment Variables Setup Guide

This guide explains how to obtain and configure all the environment variables needed for your Telegram userbot.

## Required Variables

### 1. API_ID and API_HASH

These are your Telegram API credentials that allow your application to connect to Telegram servers.

**How to get them:**

1. **Go to Telegram's Developer Portal**
   - Visit: https://my.telegram.org
   - Login with your phone number (same number you use for Telegram)

2. **Create a New Application**
   - Click on "API Development Tools"
   - Fill out the form:
     - **App title**: `My UserBot` (or any name you prefer)
     - **Short name**: `userbot` (or any short identifier)
     - **URL**: Leave empty or use your website
     - **Platform**: Choose "Desktop"
     - **Description**: `Personal Telegram UserBot`

3. **Get Your Credentials**
   - After creating the app, you'll see:
     - **App api_id**: This is your `API_ID` (numbers only)
     - **App api_hash**: This is your `API_HASH` (long string)

**Example:**
```
API_ID=12345678
API_HASH=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### 2. SESSION_STRING

This is a unique string that authenticates your userbot with your Telegram account.

**How to generate it:**

#### Method 1: Using Python Script (Recommended)

1. **Create a session generator script:**
   ```bash
   nano generate_session.py
   ```

2. **Add this code:**
   ```python
   from pyrogram import Client
   
   print("=== Telegram UserBot Session Generator ===")
   print()
   
   api_id = input("Enter your API_ID: ")
   api_hash = input("Enter your API_HASH: ")
   
   print()
   print("Please enter your phone number when prompted...")
   print("Then enter the verification code sent to your Telegram app.")
   print()
   
   with Client("my_session", api_id, api_hash) as app:
       session_string = app.export_session_string()
       print()
       print("=" * 50)
       print("SESSION STRING GENERATED SUCCESSFULLY!")
       print("=" * 50)
       print()
       print("Your session string:")
       print(session_string)
       print()
       print("IMPORTANT: Keep this session string private!")
       print("Anyone with this string can access your Telegram account.")
   ```

3. **Run the script:**
   ```bash
   python generate_session.py
   ```

4. **Follow the prompts:**
   - Enter your API_ID and API_HASH
   - Enter your phone number (with country code, e.g., +1234567890)
   - Enter the verification code sent to your Telegram app
   - Copy the generated session string

#### Method 2: Using Online Generator

1. Search for "Pyrogram session string generator"
2. Use only trusted sources (check reviews and reputation)
3. Enter your API credentials and phone number
4. Complete the verification process
5. Copy the generated session string

**Example:**
```
SESSION_STRING=BQC7aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890
```

## Optional Variables

### 3. LOG_CHAT_ID

This is the chat ID where the userbot will send startup messages and logs.

**How to get it:**

#### For Personal Chat (Saved Messages):
1. Open Telegram Web or Desktop
2. Go to "Saved Messages"
3. The URL will be like: `https://web.telegram.org/k/#@username`
4. Your user ID is your LOG_CHAT_ID (use your own user ID)

#### For a Group/Channel:
1. Add your userbot to a group or channel
2. Send a message in the group
3. Forward any message from that group to @userinfobot
4. The bot will show you the chat ID

**Example:**
```
LOG_CHAT_ID=123456789
```

### 4. BOT_PREFIX

The character(s) used to trigger commands.

**Options:**
- `.` (default) - Commands like `.alive`, `.ping`
- `!` - Commands like `!alive`, `!ping`
- `/` - Commands like `/alive`, `/ping`
- `?` - Commands like `?alive`, `?ping`

**Example:**
```
BOT_PREFIX=.
```

### 5. PM_PERMIT_ENABLED

Controls whether the PM permit system is active.

**Options:**
- `true` - Enable PM permit (default)
- `false` - Disable PM permit

**Example:**
```
PM_PERMIT_ENABLED=true
```

### 6. PM_PERMIT_LIMIT

Number of warnings before automatically blocking a user.

**Example:**
```
PM_PERMIT_LIMIT=5
```

### 7. DISABLED_PLUGINS

Comma-separated list of plugins to disable.

**Available plugins:**
- `alive`
- `pm_permit`
- `ping`
- `info`
- `stats`
- `utils`

**Example:**
```
DISABLED_PLUGINS=stats,utils
```

## Setting Up Environment Variables

### For Koyeb Deployment:

1. **During Service Creation:**
   - In the Koyeb dashboard, when creating your service
   - Go to the "Environment Variables" section
   - Add each variable with its value

2. **After Service Creation:**
   - Go to your service dashboard
   - Click on "Settings" tab
   - Scroll to "Environment Variables"
   - Add or edit variables
   - Redeploy the service

### For Local Development:

1. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file:**
   ```bash
   nano .env
   ```

3. **Add your values:**
   ```env
   # Required Variables
   API_ID=12345678
   API_HASH=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   SESSION_STRING=BQC7aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890...
   
   # Optional Variables
   BOT_PREFIX=.
   LOG_CHAT_ID=123456789
   PM_PERMIT_ENABLED=true
   PM_PERMIT_LIMIT=5
   DISABLED_PLUGINS=
   ```

### For Docker Deployment:

1. **Using docker run:**
   ```bash
   docker run -d \
     -e API_ID=12345678 \
     -e API_HASH=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 \
     -e SESSION_STRING=BQC7aBcDeFgHiJkLmNoPqRsTuVwXyZ... \
     -e BOT_PREFIX=. \
     -e LOG_CHAT_ID=123456789 \
     your-userbot-image
   ```

2. **Using docker-compose.yml:**
   ```yaml
   version: '3.8'
   services:
     userbot:
       build: .
       environment:
         - API_ID=12345678
         - API_HASH=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
         - SESSION_STRING=BQC7aBcDeFgHiJkLmNoPqRsTuVwXyZ...
         - BOT_PREFIX=.
         - LOG_CHAT_ID=123456789
         - PM_PERMIT_ENABLED=true
         - PM_PERMIT_LIMIT=5
       restart: unless-stopped
   ```

## Complete Example

Here's a complete example of all environment variables:

```env
# Required Telegram API Credentials
API_ID=12345678
API_HASH=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
SESSION_STRING=BQC7aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890

# Bot Configuration
BOT_PREFIX=.
LOG_CHAT_ID=123456789

# PM Permit Settings
PM_PERMIT_ENABLED=true
PM_PERMIT_LIMIT=5

# Plugin Management
DISABLED_PLUGINS=

# Database (Optional)
DATABASE_URL=sqlite:///userbot.db

# System Settings
TZ=UTC
PYTHONUNBUFFERED=1
```

## Security Notes

1. **Never share your credentials:**
   - Keep API_ID, API_HASH, and SESSION_STRING private
   - Don't commit them to version control
   - Don't share them in public channels

2. **Session string security:**
   - Anyone with your session string can control your Telegram account
   - Regenerate if compromised
   - Use only on trusted platforms

3. **API credentials:**
   - Each app has unique credentials
   - Don't use the same credentials across multiple bots
   - Monitor usage in Telegram's developer portal

## Troubleshooting

### Common Issues:

1. **Invalid API credentials:**
   - Double-check API_ID and API_HASH
   - Ensure no extra spaces or characters
   - Verify the app is created correctly

2. **Session string errors:**
   - Regenerate the session string
   - Ensure you used the correct API credentials when generating
   - Check for any truncation when copying

3. **Authentication errors:**
   - Verify phone number format (with country code)
   - Check if 2FA is enabled (may need app password)
   - Ensure account is not restricted

4. **Environment variable issues:**
   - Check variable names are exact (case-sensitive)
   - Ensure no trailing spaces
   - Verify platform-specific syntax

Need help? Check the main README.md file for additional troubleshooting steps.