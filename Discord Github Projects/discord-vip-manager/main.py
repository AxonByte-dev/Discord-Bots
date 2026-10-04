"""
Discord VIP Manager Bot
A bot that allows server owners to monetize VIP roles without payment gateways.

Users submit gift card codes via a modal, which logs the entry to an admin audit panel
and grants a temporary or permanent VIP role upon approval.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import discord
from discord import Interaction, User, Role
from discord.ext import commands

from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_vip_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class VIPManagerBot(commands.Bot):
    def __init__(self, database: Database):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_members = True
        intents.guild_messages = True
        
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)
        self.database = database
        self.add_listener(self.on_ready)
        self.add_listener(self.on_interaction)
        
        # Configuration
        self.vip_role_name = "VIP"
        self.gift_codes_channel = None  # Will be set from config
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for gift codes"
            )
        )
        
        # Find gift codes channel if configured
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.name == "gift-codes":
                    self.gift_codes_channel = channel
                    break
    
    async def on_interaction(self, interaction: Interaction):
        """Handle all interactions."""
        try:
            # Buttons
            if interaction.data and 'custom_id' in interaction.data:
                await self.handle_button_interaction(interaction)
                
        except Exception as e:
            logger.error(f"Error handling interaction: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while processing your request.",
                    ephemeral=True
                )
    
    async def handle_button_interaction(self, interaction: Interaction):
        """Handle button clicks."""
        custom_id = interaction.data['custom_id']
        
        if custom_id == "accept_gift":
            await self.accept_gift(interaction)
        elif custom_id == "reject_gift":
            await self.reject_gift(interaction)
    
    async def accept_gift(self, interaction: Interaction):
        """Accept a gift code and grant VIP role."""
        try:
            # Get the gift code from the interaction message
            message = interaction.message
            gift_code = None
            
            # Extract gift code from embed or message content
            for field in message.embeds[0].fields:
                if field.name.lower() == "code":
                    gift_code = field.value
                    break
            
            if not gift_code:
                await interaction.response.send_message(
                    "❌ Could not find gift code in this message.",
                    ephemeral=True
                )
                return
            
            # Get the user who submitted the code
            user_id = message.embeds[0].footer.text.split(" ")[-1]
            user = discord.utils.get(self.get_all_users(), id=int(user_id))
            
            if not user:
                await interaction.response.send_message(
                    "❌ Could not find the user who submitted this gift code.",
                    ephemeral=True
                )
                return
            
            # Find the VIP role
            guild = interaction.guild
            vip_role = discord.utils.get(guild.roles, name=self.vip_role_name)
            
            if not vip_role:
                await interaction.response.send_message(
                    "❌ VIP role not found. Please create it first.",
                    ephemeral=True
                )
                return
            
            # Grant VIP role
            try:
                await user.add_roles(vip_role, reason="VIP access via gift code approval")
                
                # Send DM to user
                dm_embed = discord.Embed(
                    title="🎉 VIP Access Granted!",
                    description=f"Your gift code has been approved! You've been granted the **{self.vip_role_name}** role.",
                    color=discord.Color.green()
                )
                dm_embed.add_field(
                    name="Code",
                    value=gift_code,
                    inline=False
                )
                dm_embed.add_field(
                    name="Approved by",
                    value=interaction.user.mention,
                    inline=True
                )
                dm_embed.add_field(
                    name="Approved at",
                    value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    inline=True
                )
                
                await user.send(embed=dm_embed)
                
                # Update database
                await self.database.update_gift_code_status(gift_code, 'approved', interaction.user.id)
                
                # Update the message to show it's been processed
                processed_embed = message.embeds[0]
                processed_embed.color = discord.Color.green()
                processed_embed.title = "✅ Gift Code Approved"
                
                await interaction.response.edit_message(embed=processed_embed)
                
                logger.info(f"Gift code {gift_code} approved by {interaction.user} for user {user.id}")
                
            except Exception as e:
                logger.error(f"Error granting VIP role: {e}")
                await interaction.response.send_message(
                    f"❌ Error granting VIP role: {e}",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error accepting gift: {e}")
            await interaction.response.send_message(
                "❌ Error accepting gift code.",
                ephemeral=True
            )
    
    async def reject_gift(self, interaction: Interaction):
        """Reject a gift code."""
        try:
            # Get the gift code from the interaction message
            message = interaction.message
            gift_code = None
            
            # Extract gift code from embed or message content
            for field in message.embeds[0].fields:
                if field.name.lower() == "code":
                    gift_code = field.value
                    break
            
            if not gift_code:
                await interaction.response.send_message(
                    "❌ Could not find gift code in this message.",
                    ephemeral=True
                )
                return
            
            # Get the user who submitted the code
            user_id = message.embeds[0].footer.text.split(" ")[-1]
            user = discord.utils.get(self.get_all_users(), id=int(user_id))
            
            if not user:
                await interaction.response.send_message(
                    "❌ Could not find the user who submitted this gift code.",
                    ephemeral=True
                )
                return
            
            # Update database
            await self.database.update_gift_code_status(gift_code, 'rejected', interaction.user.id)
            
            # Send DM to user
            dm_embed = discord.Embed(
                title="❌ Gift Code Rejected",
                description="Unfortunately, your gift code submission has been rejected.",
                color=discord.Color.red()
            )
            dm_embed.add_field(
                name="Code",
                value=gift_code,
                inline=False
            )
            dm_embed.add_field(
                name="Rejected by",
                value=interaction.user.mention,
                inline=True
            )
            dm_embed.add_field(
                name="Rejected at",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
            
            await user.send(embed=dm_embed)
            
            # Update the message to show it's been processed
            processed_embed = message.embeds[0]
            processed_embed.color = discord.Color.red()
            processed_embed.title = "🚫 Gift Code Rejected"
            
            await interaction.response.edit_message(embed=processed_embed)
            
            logger.info(f"Gift code {gift_code} rejected by {interaction.user} for user {user.id}")
            
        except Exception as e:
            logger.error(f"Error rejecting gift: {e}")
            await interaction.response.send_message(
                "❌ Error rejecting gift code.",
                ephemeral=True
            )
class GiftCodeModal(discord.ui.Modal, title="Submit Gift Code"):
    def __init__(self, bot: VIPManagerBot):
        super().__init__()
        self.bot = bot
        
        # Add gift code input field
        self.gift_code_input = discord.ui.TextInput(
            label="Gift Code",
            placeholder="Enter your Steam/Amazon gift code here",
            style=discord.TextStyle.paragraph,
            min_length=10,
            max_length=100,
            required=True,
            custom_id="gift_code"
        )
        
        self.add_item(self.gift_code_input)
    
    async def on_submit(self, interaction: Interaction):
        """Handle modal submission."""
        try:
            gift_code = self.gift_code_input.value.strip()
            
            # Find the gift codes channel
            channel = self.bot.gift_codes_channel
            if not channel:
                await interaction.response.send_message(
                    "❌ Gift codes channel not found.",
                    ephemeral=True
                )
                return
            
            # Create approval embed
            submit_embed = discord.Embed(
                title="🎫 Pending Gift Code Approval",
                description=f"{interaction.user.mention} has submitted a new gift code for review.",
                color=discord.Color.gold()
            )
            submit_embed.add_field(
                name="Code",
                value=f"`{gift_code}`",
                inline=False
            )
            submit_embed.add_field(
                name="Submitted by",
                value=f"{interaction.user.name} ({interaction.user.id})",
                inline=True
            )
            submit_embed.add_field(
                name="Submitted at",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
            submit_embed.set_footer(text=f"User ID: {interaction.user.id}")
            
            # Send the approval request
            message = await channel.send(embed=submit_embed)
            
            # Add approval buttons
            view = discord.ui.View(timeout=86400)  # 24 hours
            view.add_item(discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Accept",
                custom_id="accept_gift",
                emoji="✅",
                description="Approve and grant VIP access"
            ))
            view.add_item(discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Reject",
                custom_id="reject_gift",
                emoji="❌",
                description="Reject the submission"
            ))
            
            await message.add_reaction("✅")
            await message.add_reaction("❌")
            
            # Log to database
            await self.bot.database.log_gift_code(
                user_id=interaction.user.id,
                username=str(interaction.user),
                gift_code=gift_code,
                status='pending'
            )
            
            # Send confirmation to user
            await interaction.response.send_message(
                "✅ Your gift code has been submitted for review! An admin will approve it shortly.",
                ephemeral=True
            )
            
            logger.info(f"Gift code {gift_code} submitted by {interaction.user.id} for approval")
            
        except Exception as e:
            logger.error(f"Error submitting gift code: {e}")
            await interaction.response.send_message(
                f"❌ Error submitting gift code: {e}",
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
        
        # Initialize database
        database = Database()
        await database.init_database()
        
        # Create and run bot
        bot = VIPManagerBot(database)
        
        # Register slash commands
        @bot.tree.command(name="gift", description="Submit a gift code for VIP access")
        async def gift_command(interaction: Interaction):
            """Slash command to submit a gift code."""
            modal = GiftCodeModal(bot)
            await interaction.response.send_modal(modal)
        
        @bot.tree.command(name="review", description="Review pending gift codes")
        async def review_command(interaction: Interaction):
            """Slash command to review pending gift codes."""
            # Check if user has admin permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You don't have permission to use this command.",
                    ephemeral=True
                )
                return
            
            # Get pending gift codes
            pending_codes = await bot.database.get_pending_gift_codes()
            
            if not pending_codes:
                await interaction.response.send_message(
                    "✅ No pending gift codes to review.",
                    ephemeral=True
                )
                return
            
            # Create review embed
            review_embed = discord.Embed(
                title="📋 Gift Code Review Queue",
                description=f"There are {len(pending_codes)} pending gift codes to review.",
                color=discord.Color.blue()
            )
            
            for code in pending_codes[:10]:  # Show first 10
                review_embed.add_field(
                    name=f"Code: {code['gift_code']}",
                    value=f"Submitted by: {code['username']} ({code['user_id']})\nSubmitted at: {code['created_at']}",
                    inline=False
                )
            
            if len(pending_codes) > 10:
                review_embed.set_footer(text=f"Showing 10 of {len(pending_codes)} total")
            
            await interaction.response.send_message(embed=review_embed, ephemeral=True)
        
        # Start the bot
        logger.info("Starting Discord VIP Manager Bot...")
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