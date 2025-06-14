# Telegram UserBot

A feature-rich Telegram userbot built with Pyrogram, designed for easy deployment on Koyeb and other cloud platforms.

## Features

### Core Plugins

- **🤖 Alive Plugin** - Bot status, uptime monitoring, and system statistics
- **🛡️ PM Permit** - Auto-approval system for private messages with spam protection
- **🏓 Ping Plugin** - Network latency testing with detailed measurements
- **ℹ️ Info Plugin** - User, chat, and message information commands
- **📊 Stats Plugin** - Usage statistics and analytics
- **🔨 Utils Plugin** - Help, plugin management, logs, and system utilities

### Key Features

- **Plugin System** - Modular architecture with hot-reload capability
- **Database Integration** - SQLite for persistent data storage
- **Comprehensive Logging** - Detailed logs with database storage
- **Error Handling** - Graceful error handling throughout the application
- **Security** - PM permit system with configurable warning limits
- **Analytics** - User engagement tracking and usage statistics
- **System Monitoring** - CPU, memory, and disk usage tracking

## Commands

### Core Commands
- `.alive` - Show bot status and system information
- `.ping` - Test response time
- `.uptime` - Show bot uptime
- `.help` - Display all available commands

### PM Permit Commands
- `.approve` - Approve a user for PM
- `.disapprove` - Disapprove a user for PM
- `.block` - Block a user
- `.unblock` - Unblock a user
- `.pmguard [on/off]` - Toggle PM permit system

### Information Commands
- `.info` - Get user information
- `.id` - Get user/chat IDs
- `.chatinfo` - Get chat information
- `.msginfo` - Get message information

### Statistics Commands
- `.stats` - Show bot statistics
- `.mystats` - Show your personal statistics
- `.usage` - Show detailed usage analytics
- `.topcmds` - Show top command users

### Utility Commands
- `.plugins` - List loaded plugins
- `.logs [count]` - Show recent logs
- `.sysinfo` - Show system information
- `.eval <expression>` - Evaluate Python expression
- `.restart` - Restart the bot

## Installation & Setup

### Prerequisites

1. **Telegram API Credentials**
   - Go to https://my.telegram.org
   - Create a new application to get `API_ID` and `API_HASH`

2. **Session String**
   - Generate a session string using Pyrogram
   - You can use online generators or create one locally

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telegram-userbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the userbot**
   ```bash
   python main.py
   ```

## Deployment on Koyeb

Koyeb is a serverless platform that makes it easy to deploy applications globally. Here's how to deploy your userbot:

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial userbot setup"
   git push origin main
   ```

2. **Ensure your repository is public** (or set up private repository access)

### Step 2: Create Koyeb Account

1. Go to [koyeb.com](https://www.koyeb.com)
2. Sign up for a free account
3. Verify your email address

### Step 3: Deploy the Application

1. **Create a new service**
   - Click "Create Service" in the Koyeb dashboard
   - Select "GitHub" as the source

2. **Connect GitHub repository**
   - Authorize Koyeb to access your GitHub account
   - Select your userbot repository
   - Choose the main branch

3. **Configure build settings**
   - **Build command**: `pip install -r requirements.txt` (optional, auto-detected)
   - **Run command**: `python main.py`
   - **Port**: Leave empty (userbot doesn't need a web server)

4. **Set environment variables**
   Add these required environment variables:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   SESSION_STRING=your_session_string
   BOT_PREFIX=.
   PM_PERMIT_ENABLED=true
   PM_PERMIT_LIMIT=5
   ```

   Optional environment variables:
   ```
   LOG_CHAT_ID=your_log_chat_id
   DISABLED_PLUGINS=plugin1,plugin2
   DATABASE_URL=sqlite:///userbot.db
   ```

5. **Advanced settings**
   - **Instance type**: Select "nano" for free tier
   - **Regions**: Choose your preferred region
   - **Scaling**: Set min/max instances to 1

6. **Deploy**
   - Click "Deploy" to start the deployment
   - Wait for the build and deployment to complete

### Step 4: Monitor Deployment

1. **Check logs**
   - Go to your service dashboard
   - Click on "Logs" to see real-time logs
   - Verify the userbot starts successfully

2. **Verify functionality**
   - Send a message to your userbot in Telegram
   - Try basic commands like `.alive` or `.ping`
   - Check that PM permit is working if enabled

### Step 5: Domain Configuration (Optional)

If you want a custom domain:
1. Go to "Domains" in your service settings
2. Add your custom domain
3. Update DNS records as instructed

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API Hash | `abcdef1234567890abcdef1234567890` |
| `SESSION_STRING` | Pyrogram session string | `BQC7aBc...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_PREFIX` | Command prefix | `.` |
| `LOG_CHAT_ID` | Chat ID for logs | None |
| `PM_PERMIT_ENABLED` | Enable PM permit | `true` |
| `PM_PERMIT_LIMIT` | Warning limit | `5` |
| `DATABASE_URL` | Database URL | `sqlite:///userbot.db` |
| `DISABLED_PLUGINS` | Disabled plugins | Empty |

## Generating Session String

You need a session string to authenticate with Telegram. Here are several methods:

### Method 1: Using Pyrogram Script

Create a file `generate_session.py`:

```python
from pyrogram import Client

api_id = int(input("Enter API ID: "))
api_hash = input("Enter API Hash: ")

with Client("my_account", api_id, api_hash) as app:
    print(f"Session String: {app.export_session_string()}")
```

Run it:
```bash
python generate_session.py
```

### Method 2: Online Generators

Use trusted online session string generators:
- Search for "Pyrogram session string generator"
- Use only trusted sources
- Never share your session string

## Troubleshooting

### Common Issues

1. **Configuration errors**
   - Ensure all required environment variables are set
   - Verify API credentials are correct
   - Check session string validity

2. **Database errors**
   - Check if SQLite is supported on your platform
   - Verify write permissions for database file

3. **Plugin errors**
   - Check plugin-specific logs
   - Verify plugin dependencies are installed
   - Disable problematic plugins using `DISABLED_PLUGINS`

### Koyeb-Specific Issues

1. **Build failures**
   - Check Python version compatibility
   - Verify requirements.txt is correct
   - Review build logs for specific errors

2. **Runtime errors**
   - Check service logs in Koyeb dashboard
   - Verify environment variables are set correctly
   - Monitor resource usage

3. **Free tier limitations**
   - 100 hours per month compute time
   - Automatic sleep after inactivity
   - Limited to 1 concurrent instance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Security Notes

- Never commit API credentials to version control
- Use environment variables for sensitive data
- Keep your session string private
- Regularly update dependencies
- Monitor logs for suspicious activity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review Koyeb documentation
- Open an issue in the repository

## Disclaimer

This userbot is for educational and personal use only. Users are responsible for complying with Telegram's Terms of Service and applicable laws. The developers are not responsible for any misuse of this software.