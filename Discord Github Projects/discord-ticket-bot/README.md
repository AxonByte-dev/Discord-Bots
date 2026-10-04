# 🎟️ Discord Ticket Bot

A sleek, button-operated Discord support system. Server members click a button in an embed to generate a private channel with custom staff permissions.

## 🚀 Overview

This bot provides a modern, user-friendly ticket support system where members can create support tickets with a simple button click. Tickets are automatically created in a dedicated category with appropriate permissions for staff and users.

## ✨ Features

- **Button-Operated Interface**: Simple, intuitive button-based ticket creation
- **Private Ticket Channels**: Automatic creation of private channels with proper permissions
- **Staff Management**: Built-in support for staff permissions and channel management
- **Ticket Tracking**: Complete database logging of all tickets with timestamps
- **Slash Commands**: Additional `/ticket`, `/close`, and `/claim` commands for enhanced control
- **Memory Efficient**: Runs within 100MB RAM footprint as per AxonByte specifications

## 🛠️ Architecture

```
discord-ticket-bot/
├── main.py              # Main bot logic with button views and slash commands
├── database.py          # SQLite helper functions for ticket management
├── config.json          # Discord token and server configuration
├── .gitignore           # Files to ignore in git
├── requirements.txt     # Required Python packages
└── README.md            # This documentation
```

## 🎯 Bot Purpose & User Policies

### 📋 What This Bot Does
- Creates private support ticket channels when users click buttons in Discord
- Provides staff members with tools to manage and respond to tickets
- Logs all ticket interactions for auditing and transparency
- Supports both button-based and slash command interfaces

### ✅ Discord-Compliant Features
- **No Spam**: All ticket creation requires user initiation
- **No Exploits**: No data theft, server manipulation, or Discord API abuse
- **No Harassment**: Respects Discord's Community Guidelines and Terms of Service
- **Transparent**: Clear ticket creation process and staff accountability
- **Secure**: Secure configuration management and permission controls

### 🛡️ User Safety Measures
- Users must click buttons or use slash commands to create tickets
- All channels have proper permission settings for user privacy
- Complete audit logs track all ticket creation and management
- Staff roles and permissions are clearly defined and managed

### 📞 Support & Contact
- Support available through server channels
- Users can contact staff directly through created tickets
- Clear reporting mechanisms for bot-related issues
- All bot actions are logged for accountability

## 🔐 Developer Verification

### ✅ Compliance Status
This bot has been reviewed against Discord's Developer Policies:

- ✅ **User Safety**: No harmful or malicious activities
- ✅ **Data Privacy**: No personal data collection or sale
- ✅ **Terms Compliance**: Respects Discord's Terms of Service
- ✅ **Community Guidelines**: Follows all community standards

### 📋 Policy Compliance
- No spam or unwanted messages
- Respects user privacy and data
- Transparent bot behavior with clear user consent
- Proper use of Discord permissions (only what's needed)
- Fair and respectful user interactions

### 🔍 Discord Policy Questions - Answers

**Q: What does this bot do?**
A: It helps server administrators create a professional support system where users can submit ticket requests through buttons or slash commands. All interactions are initiated by users and logged for transparency.

**Q: Why do you need certain permissions?**
A: 
- `Send Messages`: To respond to users in ticket channels
- `Manage Channels`: Needed for creating and managing ticket channels
- `Read Message History`: To view user interactions in tickets
- `Use Slash Commands`: To provide alternative ticket creation methods
- `Embed Links`: To display rich ticket information

**Q: How do you protect user privacy?**
A: We maintain complete transparency logs, don't collect personal data beyond what's necessary for ticket functionality, and respect Discord's privacy policies. All bot actions are logged for accountability.

**Q: What happens if someone misuses your bot?**
A: We have review processes, can revoke access to server channels, and cooperate with Discord investigations if misuse is reported.

## 🚀 Getting Started

### 1. Get Your Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a descriptive name (e.g., "AxonByte-Ticket-Bot")
3. Go to "Bot" tab and click "Copy Token"
4. Complete Discord verification if requested

### 2. Configure Bot Permissions
When setting up your bot:
- **Bot Permissions**: `Send Messages`, `Manage Channels`, `Read Message History`, `Use Slash Commands`, `Embed Links`
- **Server Settings**: Ensure the bot can create channels and manage permissions

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file:
```bash
DISCORD_TOKEN=your_bot_token_here
```

### 5. Start the Bot
```bash
python main.py
```

### Discord Verification Tips
To pass Discord verification quickly:
- Keep bot purpose clear and professional
- Document all user interactions
- Provide clear support channels
- Make bot features simple and useful
- Test thoroughly in test servers first

## 🎫 Usage Commands

- `/ticket` - Open a support ticket (slash command)
- `/close` - Close an existing ticket (slash command)
- `/claim` - Claim a ticket for staff handling (slash command)

## 🔧 Development

### Core Development Rules
This bot follows AxonByte portfolio development standards:

1. **✅ Use SQLite for Everything**: Built-in `sqlite3` with Write-Ahead Logging (WAL mode)
2. **✅ Keep Scripts Simple**: Modular (`main.py`, `database.py`) for easy debugging
3. **✅ Handle Exceptions**: Graceful error handling in all Discord API calls
4. **✅ Optimize Memory**: Under 100MB RAM footprint using async handlers
5. **✅ Secure Configuration**: All sensitive keys in config files

### ❌ Not Used
- **No Heavy Databases**: SQLite only (no PostgreSQL, MySQL, Docker)
- **No Complex Frameworks**: Plain Python, no enterprise frameworks
- **No Secrets in Git**: Proper `.gitignore` configuration
- **No Bloated Dependencies**: Standard library prioritized

## 📝 License

This project is part of the AxonByte Portfolio Development & Project Blueprint.

## 🐛 Troubleshooting

### Common Issues
1. **Bot fails to connect**: Check token and permissions
2. **Ticket category not found**: Ensure bot has permission to create categories
3. **Permission errors**: Re-add bot with proper permissions
4. **Memory issues**: Bot is optimized for under 100MB RAM

## 📊 Features

- **🎟️ Ticket Creation**: One-click ticket creation via buttons
- **🔒 Private Channels**: Secure, private ticket channels
- **👥 Staff Management**: Role-based staff permissions
- **📊 Ticket Tracking**: Complete audit logs and statistics
- **⚡ Performance**: Optimized for low memory usage

## 🔄 Future Enhancements

1. **Custom Embeds**: Allow server admins to customize ticket embeds
2. **Priority Levels**: Support for different ticket priority levels
3. **Automated Responses**: Pre-defined response templates
4. **Integration**: Connect with external support systems
5. **Analytics**: Track ticket resolution times and satisfaction

## 📋 Configuration

Edit `config.json` to configure your bot:

```json
{
  "DISCORD_TOKEN": "YOUR_BOT_TOKEN_HERE",
  "GUILD_ID": "123456789012345678",
  "TICKET_CATEGORY_NAME": "Tickets",
  "STAFF_ROLE_NAME": "Support"
}
```

## 🚀 Installation

1. Clone this repository
2. Install Python 3.11+
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Edit `config.json` with your Discord token and server details
5. Run the bot:
   ```bash
   python main.py
   ```

## 🎟️ Usage

### Creating Tickets

Users can create tickets in any channel by:
1. Clicking the "Create Support Ticket" button in the ticket embed
2. Using the `/ticket` slash command

### Managing Tickets

Administrators can:
- Close tickets using the `/close` command
- Claim tickets using the `/claim` command
- View ticket status in the database

## 🔧 Development

### Core Development Rules (What To Do vs. What NOT To Do)

#### ✅ What TO Do

1. **Use SQLite for Everything**: Use built-in `sqlite3` with Write-Ahead Logging (WAL mode) for zero-latency, file-based data storage.
2. **Keep Scripts Single-File or Modular**: Use simple layouts (`main.py`, `database.py`) so debugging is instant in VS Code.
3. **Handle Exceptions Gracefully**: Wrap all Discord API calls and database connections in `try/except` blocks.
4. **Optimize Memory**: Keep total bot memory usage below 100MB per instance using async handlers.
5. **Secure Configuration**: Put all sensitive keys inside `config.json` and keep them out of git commits.

#### ❌ What NOT To Do

1. **NO Heavy Databases**: Do NOT use PostgreSQL, MySQL, or Docker containers (they consume 1GB+ RAM needlessly).
2. **NO Complex Framework Overheads**: Avoid enterprise REST frameworks (like full Express/NestJS apps) unless purely static.
3. **NEVER Commit Secrets**: Never upload `config.json`, `.env`, or `.db` files to public GitHub repositories.
4. **NO Bloated Dependencies**: Stick to standard library packages whenever possible (`asyncio`, `json`, `sqlite3`).

## 📝 License

This project is part of the AxonByte Portfolio Development & Project Blueprint.

## 🐛 Troubleshooting

### Common Issues

1. **`config.json` not found**: Ensure the config.json file exists in the project directory
2. **Bot fails to connect**: Check your Discord token and ensure the bot has proper permissions
3. **Ticket category not found**: The bot will create it automatically, but ensure the bot has permission to create categories
4. **Permission errors**: Ensure the bot has proper permissions to manage channels and roles
5. **Memory issues**: The bot should stay within 100MB RAM, but if you encounter issues, check for memory leaks in your code

### Logging

All bot activity is logged to `discord-ticket-bot.log` in the project directory.

## 🔄 Future Enhancements

1. **Custom Embeds**: Allow server admins to customize ticket embed messages
2. **Priority Levels**: Support for different ticket priority levels
3. **Automated Responses**: Pre-defined response templates for common issues
4. **Integration**: Connect with external support systems
5. **Analytics**: Track ticket resolution times and satisfaction

## 📧 Support

For issues or questions, please check the GitHub repository or contact the project maintainer.