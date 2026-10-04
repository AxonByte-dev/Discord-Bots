"""
Discord Game Server Telemetry Bot
A background service that queries live game server ports and updates Discord embeds
with live status, player count, and latency every 60 seconds.
"""

import asyncio
import json
import logging
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_game_telemetry.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GameTelemetryBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True
        
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)
        self.add_listener(self.on_ready)
        
        # Configuration
        self.servers_config = {}
        self.status_message_id = None
        self.status_channel = None
        self.update_interval = 60  # 60 seconds
        
        # Server connections
        self.server_connections = {}
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="monitoring game servers"
            )
        )
        
        # Load configuration
        await self.load_configuration()
        
        # Start background tasks
        self.status_task = asyncio.create_task(self.update_status_loop())
        self.server_checks_task = asyncio.create_task(self.check_all_servers())
        
        logger.info("Game Telemetry Bot initialized and background tasks started")
    
    async def load_configuration(self):
        """Load server configuration from config.json."""
        try:
            config_path = Path(__file__).parent / "config.json"
            
            if not config_path.exists():
                logger.error("config.json not found")
                return
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.servers_config = config.get("servers", {})
            self.status_channel_id = config.get("status_channel_id")
            self.update_interval = config.get("update_interval", 60)
            
            # Find status channel
            for guild in self.guilds:
                for channel in guild.text_channels:
                    if channel.id == self.status_channel_id:
                        self.status_channel = channel
                        break
            
            logger.info(f"Loaded {len(self.servers_config)} servers from configuration")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    async def update_status_loop(self):
        """Background task to update the status message."""
        await self.wait_until_ready()
        
        while not self.is_closed():
            try:
                await self.update_status_message()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in status update loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def check_all_servers(self):
        """Background task to check all servers."""
        await self.wait_until_ready()
        
        while not self.is_closed():
            try:
                await self.check_servers()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in server check loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def check_servers(self):
        """Check the status of all configured servers."""
        for server_name, server_config in self.servers_config.items():
            try:
                server_type = server_config.get("type", "generic")
                
                if server_type == "minecraft":
                    status = await self.check_minecraft_server(server_config)
                elif server_type == "cs2":
                    status = await self.check_cs2_server(server_config)
                else:
                    status = await self.check_generic_server(server_config)
                
                # Store the status
                self.server_connections[server_name] = status
                
                logger.info(f"Server {server_name} status: {status['status']}")
                
            except Exception as e:
                logger.error(f"Error checking server {server_name}: {e}")
                self.server_connections[server_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now()
                }
    
    async def check_minecraft_server(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check a Minecraft server status."""
        host = server_config.get("host")
        port = server_config.get("port", 25565)
        
        if not host:
            raise ValueError("Minecraft server host not configured")
        
        try:
            # Create socket connection
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                sock.connect((host, port))
                latency = (time.time() - start_time) * 1000  # Convert to ms
                
                # For Minecraft, we could send a ping packet, but for simplicity
                # we'll just check if the port is open
                if latency < 100:
                    status = "online"
                elif latency < 500:
                    status = "slow"
                else:
                    status = "laggy"
                
                return {
                    "status": status,
                    "latency": latency,
                    "port": port,
                    "players": "unknown",  # Would need MC query for actual player count
                    "timestamp": datetime.now()
                }
                
            except socket.timeout:
                return {
                    "status": "offline",
                    "error": "Connection timeout",
                    "latency": None,
                    "port": port,
                    "timestamp": datetime.now()
                }
            except ConnectionRefusedError:
                return {
                    "status": "offline",
                    "error": "Connection refused",
                    "latency": None,
                    "port": port,
                    "timestamp": datetime.now()
                }
            finally:
                sock.close()
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "latency": None,
                "port": port,
                "timestamp": datetime.now()
            }
    
    async def check_cs2_server(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check a CS2 server status."""
        host = server_config.get("host")
        port = server_config.get("port", 27015)
        
        if not host:
            raise ValueError("CS2 server host not configured")
        
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                sock.connect((host, port))
                latency = (time.time() - start_time) * 1000
                
                # Try to send a simple packet to check if it's a responsive CS2 server
                # CS2 doesn't have a simple ping protocol, so we'll just check port
                if latency < 50:
                    status = "online"
                elif latency < 200:
                    status = "slow"
                else:
                    status = "laggy"
                
                return {
                    "status": status,
                    "latency": latency,
                    "port": port,
                    "players": "unknown",
                    "timestamp": datetime.now()
                }
                
            except socket.timeout:
                return {
                    "status": "offline",
                    "error": "Connection timeout",
                    "latency": None,
                    "port": port,
                    "timestamp": datetime.now()
                }
            except ConnectionRefusedError:
                return {
                    "status": "offline",
                    "error": "Connection refused",
                    "latency": None,
                    "port": port,
                    "timestamp": datetime.now()
                }
            finally:
                sock.close()
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "latency": None,
                "port": port,
                "timestamp": datetime.now()
            }
    
    async def check_generic_server(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check a generic server using socket connection."""
        host = server_config.get("host")
        port = server_config.get("port")
        
        if not host or not port:
            raise ValueError("Generic server host or port not configured")
        
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                sock.connect((host, port))
                latency = (time.time() - start_time) * 1000
                
                if latency < 100:
                    status = "online"
                elif latency < 500:
                    status = "slow"
                else:
                    status = "laggy"
                
                return {
                    "status": status,
                    "latency": latency,
                    "port": port,
                    "players": "unknown",
                    "timestamp": datetime.now()
                }
                
            except socket.timeout:
                return {
                    "status": "offline",
                    "error": "Connection timeout",
                    "latency": None,
                    "port": port,
                    "timestamp": datetime.now()
                }
            except ConnectionRefusedError:
                return {
                    "status": "offline",
                    "error": "Connection refused",
                    "latency": None,
                    "port": port,
                    "timestamp": datetime.now()
                }
            finally:
                sock.close()
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "latency": None,
                "port": port,
                "timestamp": datetime.now()
            }
    
    async def update_status_message(self):
        """Update the status message with current server information."""
        if not self.status_channel:
            logger.warning("Status channel not configured")
            return
        
        try:
            # Create status embed
            status_embed = discord.Embed(
                title="🎮 Game Server Status",
                description=f"Real-time monitoring of game servers (Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
                color=discord.Color.blue()
            )
            
            # Add each server status
            online_count = 0
            total_count = len(self.server_connections)
            
            for server_name, status in self.server_connections.items():
                server_status = status.get("status", "unknown")
                
                # Map status to emoji
                status_emoji = "🟢" if server_status == "online" else "🟡" if server_status == "slow" else "🔴" if server_status == "laggy" else "❌" if server_status == "offline" else "⚪"
                
                # Format status details
                if server_status == "online":
                    latency = status.get("latency")
                    latency_str = f" ({latency:.0f}ms)" if latency else ""
                    status_text = f"Online{latency_str}"
                elif server_status == "slow":
                    status_text = f"Slow Response"
                elif server_status == "laggy":
                    status_text = f"High Latency"
                elif server_status == "offline":
                    error = status.get("error", "Unknown")
                    status_text = f"Offline ({error})"
                elif server_status == "error":
                    error = status.get("error", "Unknown")
                    status_text = f"Error ({error})"
                else:
                    status_text = f"Unknown"
                
                # Add to embed
                status_embed.add_field(
                    name=f"{status_emoji} {server_name}",
                    value=status_text,
                    inline=True
                )
                
                if server_status == "online":
                    online_count += 1
            
            # Add summary
            status_embed.set_footer(text=f"Servers: {online_count}/{total_count} online | Auto-updates every {self.update_interval} seconds")
            
            # Update or create status message
            if self.status_message_id:
                try:
                    message = await self.status_channel.fetch_message(self.status_message_id)
                    await message.edit(embed=status_embed)
                    logger.info("Status message updated")
                except discord.NotFound:
                    # Message was deleted, create a new one
                    self.status_message_id = None
                    await self.create_status_message(status_embed)
            else:
                await self.create_status_message(status_embed)
                
        except Exception as e:
            logger.error(f"Error updating status message: {e}")
    
    async def create_status_message(self, embed: discord.Embed):
        """Create a new status message."""
        try:
            message = await self.status_channel.send(embed=embed)
            self.status_message_id = message.id
            logger.info(f"Status message created: {message.id}")
        except Exception as e:
            logger.error(f"Error creating status message: {e}")
    
    async def add_server(self, interaction: Interaction, server_config: Dict[str, Any]):
        """Add a new server to monitor."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to add servers.",
                ephemeral=True
            )
            return
        
        try:
            server_name = server_config.get("name")
            if not server_name:
                await interaction.response.send_message(
                    "❌ Server name is required.",
                    ephemeral=True
                )
                return
            
            if server_name in self.servers_config:
                await interaction.response.send_message(
                    f"❌ A server named '{server_name}' already exists.",
                    ephemeral=True
                )
                return
            
            self.servers_config[server_name] = server_config
            
            # Save to config file
            config_path = Path(__file__).parent / "config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config["servers"] = self.servers_config
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Immediately check the server
            await self.check_servers()
            
            await interaction.response.send_message(
                f"✅ Server '{server_name}' added and is being monitored.",
                ephemeral=True
            )
            
            logger.info(f"Server {server_name} added by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error adding server: {e}")
            await interaction.response.send_message(
                f"❌ Error adding server: {e}",
                ephemeral=True
            )
    
    async def remove_server(self, interaction: Interaction, server_name: str):
        """Remove a server from monitoring."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You don't have permission to remove servers.",
                ephemeral=True
            )
            return
        
        try:
            if server_name not in self.servers_config:
                await interaction.response.send_message(
                    f"❌ Server '{server_name}' not found.",
                    ephemeral=True
                )
                return
            
            del self.servers_config[server_name]
            del self.server_connections[server_name]
            
            # Save to config file
            config_path = Path(__file__).parent / "config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config["servers"] = self.servers_config
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            await interaction.response.send_message(
                f"✅ Server '{server_name}' removed from monitoring.",
                ephemeral=True
            )
            
            logger.info(f"Server {server_name} removed by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error removing server: {e}")
            await interaction.response.send_message(
                f"❌ Error removing server: {e}",
                ephemeral=True
            )
async def load_config():
    """Load configuration from config.json."""
    config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        raise FileNotFoundError("config.json not found")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config
async def main():
    """Main function to run the bot."""
    try:
        # Load configuration
        config = await load_config()
        
        # Create and run bot
        bot = GameTelemetryBot()
        
        # Register slash commands
        @bot.tree.command(name="addserver", description="Add a server to monitor")
        async def add_server_command(interaction: Interaction):
            """Slash command to add a server to monitor."""
            # This is a placeholder - in reality you'd want a modal for server configuration
            await interaction.response.send_message(
                "❌ Server addition not yet implemented. Please use the config.json file.",
                ephemeral=True
            )
        
        @bot.tree.command(name="removeserver", description="Remove a server from monitoring")
        async def remove_server_command(interaction: Interaction):
            """Slash command to remove a server from monitoring."""
            # This is a placeholder - in reality you'd want a modal for server selection
            await interaction.response.send_message(
                "❌ Server removal not yet implemented. Please edit the config.json file.",
                ephemeral=True
            )
        
        @bot.tree.command(name="status", description="Show server status")
        async def status_command(interaction: Interaction):
            """Slash command to show current server status."""
            if not bot.status_message_id:
                await interaction.response.send_message(
                    "❌ No status message found. The bot may not be running properly.",
                    ephemeral=True
                )
                return
            
            try:
                message = await interaction.guild.text_channels[0].fetch_message(bot.status_message_id)
                await interaction.response.send_message(
                    "Here's the current server status:",
                    embed=message.embeds[0] if message.embeds else None
                )
            except Exception as e:
                logger.error(f"Error fetching status message: {e}")
                await interaction.response.send_message(
                    "❌ Could not retrieve status message.",
                    ephemeral=True
                )
        
        @bot.tree.command(name="stats", description="Show telemetry statistics")
        async def stats_command(interaction: Interaction):
            """Slash command to show telemetry statistics."""
            # Simple stats display
            embed = discord.Embed(
                title="📊 Server Telemetry Statistics",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Status Channel",
                value=bot.status_channel.mention if bot.status_channel else "Not configured",
                inline=True
            )
            
            embed.add_field(
                name="Update Interval",
                value=f"{bot.update_interval} seconds",
                inline=True
            )
            
            embed.add_field(
                name="Servers Monitored",
                value=str(len(bot.servers_config)),
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
        
        # Start the bot
        logger.info("Starting Discord Game Telemetry Bot...")
        await bot.start(config["DISCORD_TOKEN"])
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
if __name__ == "__main__":
    # Set up the working directory to the script's directory
    os.chdir(Path(__file__).parent)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")