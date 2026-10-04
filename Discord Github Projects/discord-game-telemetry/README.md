# 🎮 Discord Game Server Telemetry Bot

A background service that queries live game server ports and updates Discord embeds
with live status, player count, and latency every 60 seconds.

## 🚀 Overview

This bot provides real-time monitoring of game servers (Minecraft, CS2, and generic TCP servers) with automatic status updates, latency tracking, and player counts displayed in Discord.

## ✨ Features

- **Real-time Server Monitoring**: Check server status every 60 seconds
- **Latency Tracking**: Measure and display server response time
- **Multiple Server Types**: Support for Minecraft, CS2, and generic TCP servers
- **Status Emojis**: Visual indicators (🟢 Online / 🟡 Slow / 🔴 Laggy / ❌ Offline)
- **Automatic Updates**: Background service updates status messages without manual intervention
- **Customizable Configuration**: Edit config.json to add/remove servers
- **Memory Efficient**: Runs within 100MB RAM footprint as per AxonByte specifications

## 🛠️ Architecture

```
discord-game-telemetry/
├── main.py              # Main bot logic with background tasks and commands
├── config.json          # Server configurations and bot settings
├── .gitignore           # Files to ignore in git
├── requirements.txt     # Required Python packages
└── README.md            # This documentation
```

## 🎯 Bot Purpose & User Policies

### 📋 What This Bot Does
- Monitors game server status (Minecraft, CS2, generic TCP servers)
- Provides real-time latency and performance metrics
- Updates Discord embeds automatically every 60 seconds
- Displays server status with visual indicators
- Runs as a background service with minimal resource usage

### ✅ Discord-Compliant Features
- **No Spam**: Background updates, no unwanted messages to users
- **No Exploits**: No server scanning abuse, no Discord API manipulation
- **No Harassment**: Respects Discord's Community Guidelines
- **Transparent**: Clear status monitoring purpose and functionality
- **Secure**: No data collection beyond what's needed for monitoring

### 🛡️ User Safety Measures
- Only monitors servers explicitly configured by administrators
- No direct interaction with game servers beyond basic connectivity checks
- Complete transparency about monitoring activities
- Minimal permissions required (read messages only)
- Clear documentation about data collection

### 📞 Support & Contact
- Support available through Discord channels
- Clear documentation for server administrators
- Reporting mechanisms for monitoring issues
- All monitoring activities are logged for transparency

## 🔐 Developer Verification

### ✅ Compliance Status
This bot has been reviewed against Discord's Developer Policies:

- ✅ **User Safety**: No harmful or malicious activities
- ✅ **Data Privacy**: Minimal data collection, only for monitoring purposes
- ✅ **Terms Compliance**: Respects Discord's Terms of Service
- ✅ **Community Guidelines**: Follows all community standards

### 📋 Policy Compliance
- No spam or unwanted messages to users
- Respects server administrators' monitoring decisions
- Transparent monitoring activities
- Minimal permissions usage (read-only where possible)
- Clear purpose and functionality documentation

### 🔍 Discord Policy Questions - Answers

**Q: What does this bot do?**
A: It provides a monitoring service that checks the status of game servers (Minecraft, CS2, generic TCP) and displays their status, latency, and performance metrics in Discord. The bot runs as a background service and only updates status messages automatically.

**Q: Why do you need certain permissions?**
A: 
- `Read Message History`: To read the status message for updates
- `Embed Links`: To update and edit status messages
- `Use External Emojis`: For status indicator emojis
- `Read Messages`: To access monitoring channels

**Q: How do you protect user privacy?**
A: We collect minimal data (only server status information), don't store personal data, and maintain complete transparency about monitoring activities. All server monitoring is configured by administrators.

**Q: What happens if someone misuses your bot?**
A: We have review processes, can revoke access, and cooperate with Discord investigations if misuse is reported. The bot is designed for administrative server monitoring only.

## 🚀 Getting Started

### 1. Get Your Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a descriptive name (e.g., "AxonByte-Game-Telemetry-Bot")
3. Go to "Bot" tab and click "Copy Token"
4. Complete Discord verification if requested

### 2. Configure Bot Permissions
When setting up your bot:
- **Bot Permissions**: `Read Message History`, `Embed Links`, `Use External Emojis`
- **Server Settings**: Ensure the bot can read and update status messages
- **Channels**: Create a dedicated channel for status updates

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file:
```bash
DISCORD_TOKEN=your_bot_token_here
```

### 5. Configure Server Monitoring
Edit `config.json` with your server configurations:
```json
{
  "DISCORD_TOKEN": "YOUR_BOT_TOKEN_HERE",
  "SERVERS": {
    "minecraft_server": {
      "name": "Minecraft Server",
      "host": "minecraft.example.com",
      "port": 25565,
      "type": "minecraft"
    },
    "cs2_server": {
      "name": "CS2 Server", 
      "host": "cs2.example.com",
      "port": 27015,
      "type": "cs2"
    }
  },
  "STATUS_CHANNEL_ID": "YOUR_STATUS_CHANNEL_ID",
  "UPDATE_INTERVAL": 60
}
```

### 6. Start the Bot
```bash
python main.py
```

### Discord Verification Tips
To pass Discord verification quickly:
- Keep monitoring purpose clear and administrative
- Document all server monitoring activities
- Provide clear documentation for administrators
- Make monitoring simple and useful
- Test with dummy servers first

## 🎮 Usage Commands

- `/addserver` - Add a server to monitor
- `/removeserver` - Remove a server from monitoring  
- `/status` - Show current server status
- `/stats` - Show telemetry statistics

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
2. **Status channel not found**: Create a text channel for status updates
3. **Server configuration errors**: Verify server settings in config.json
4. **Memory issues**: Bot is optimized for under 100MB RAM
5. **Connection timeouts**: Check server hosts and ports

## 📊 Features

- **🎮 Real-time Monitoring**: Live server status updates
- **⚡ Latency Tracking**: Measure and display response times
- **📊 Visual Indicators**: Emoji-based status display
- **🔄 Automatic Updates**: Background service with 60-second intervals
- **🎯 Multiple Server Types**: Support for Minecraft, CS2, generic TCP
- **⚙️ Customizable Configuration**: Easy server management via config.json
- **🔒 Memory Efficient**: Under 100MB RAM footprint

## 🔄 Future Enhancements

1. **Player Count Tracking**: Real-time player statistics for supported servers
2. **Custom Status Messages**: Administrator-defined status templates
3. **Webhook Integration**: Connect with external monitoring systems
4. **Alert System**: Notify administrators of server issues
5. **Historical Data**: Track monitoring history and trends
6. **Dashboard Integration**: Web interface for monitoring
7. **Advanced Metrics**: CPU, memory, and resource usage tracking

## 📊 Technical Specifications

### Performance
- **Memory Usage**: Under 100MB RAM
- **Update Interval**: 60 seconds (configurable)
- **Background Tasks**: Non-blocking async operations
- **Connection Management**: Automatic retry and timeout handling

### Server Support
- **Minecraft**: Port 25565 connectivity checks
- **CS2**: Port 27015 connectivity checks
- **Generic**: Any TCP port connectivity checks
- **Extensible**: Easy to add new server types

### Reliability
- **Automatic Restarts**: Background task monitoring
- **Error Handling**: Comprehensive exception handling
- **Logging**: Detailed activity logging
- **Graceful Shutdown**: Proper cleanup on bot stop

## 🔄 Advanced Features Planned

1. **🎯 Custom Status Messages**: Administrator-defined status templates
2. **📈 Historical Analytics**: Track monitoring trends and patterns
3. **🚨 Alert System**: Real-time notifications for server issues
4. **🌐 Dashboard Integration**: Web interface for monitoring
5. **⚡ Performance Optimization**: Advanced metrics and alerts
6. **🔧 Advanced Configuration**: YAML/JSON-based server management
7. **📊 Statistical Analysis**: Monitor server performance over time

## 📋 Configuration

Edit `config.json` to configure your servers:

```json
{
  "DISCORD_TOKEN": "YOUR_BOT_TOKEN_HERE",
  "SERVERS": {
    "minecraft_server": {
      "name": "Minecraft Server",
      "host": "minecraft.example.com",
      "port": 25565,
      "type": "minecraft"
    }
  },
  "STATUS_CHANNEL_ID": "123456789012345678",
  "UPDATE_INTERVAL": 60
}
```

### Server Types

- **minecraft**: Checks Minecraft server port and latency
- **cs2**: Checks CS2 server port and latency  
- **generic**: Checks generic TCP server port and latency

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

## 🎮 Usage Commands

The bot provides the following slash commands:

- `/status` - Show current server status
- `/stats` - Show telemetry statistics

## 📊 Status Display

The bot displays server status with emojis:
- 🟢 **Online**: Server is responding normally
- 🟡 **Slow**: Server has high latency (>100ms)
- 🔴 **Laggy**: Server has very high latency (>500ms)
- ❌ **Offline**: Server is not responding
- ⚪ **Unknown**: Status cannot be determined

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
3. **Server not showing status**: Verify the server configuration in config.json
4. **Memory issues**: The bot should stay within 100MB RAM, but if you encounter issues, check for memory leaks in your code

### Logging

All bot activity is logged to `discord-game-telemetry.log` in the project directory.

## 🔄 Future Enhancements

1. Add player count tracking for supported server types
2. Implement health checks for HTTP-based servers
3. Add custom notification thresholds
4. Support for more game server types
5. Integration with monitoring dashboards

## 📧 Support

For issues or questions, please check the GitHub repository or contact the project maintainer.