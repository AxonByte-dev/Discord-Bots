"""
Discord Ticket Bot
A sleek, button-operated Discord support system.

This bot creates private ticket channels when users click a button.
"""

import asyncio
import json
import logging
import os
from pathlib import Path

import discord
from discord import Interaction, SelectOption
from discord.ext import commands

from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_ticket_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TicketBot(commands.Bot):
    def __init__(self, database: Database):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.guild_members = True
        
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)
        self.database = database
        self.add_listener(self.on_ready)
        self.add_listener(self.on_interaction)
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="for support tickets"
            )
        )
    
    async def on_interaction(self, interaction: Interaction):
        """Handle all interactions."""
        try:
            # Buttons
            if interaction.data and 'custom_id' in interaction.data:
                await self.handle_button_interaction(interaction)
            
            # Select menus
            if interaction.data and 'component_type' in interaction.data and interaction.data['component_type'] == 3:
                await self.handle_select_interaction(interaction)
                
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
        
        if custom_id == "create_ticket":
            await self.create_ticket(interaction)
        elif custom_id == "close_ticket":
            await self.close_ticket(interaction)
        elif custom_id == "claim_ticket":
            await self.claim_ticket(interaction)
    
    async def create_ticket(self, interaction: Interaction):
        """Create a new ticket channel for the user."""
        user = interaction.user
        guild = interaction.guild
        
        if not guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        
        # Get or create ticket category
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            try:
                category = await guild.create_category(
                    name="Tickets",
                    reason="Created for support tickets"
                )
            except Exception as e:
                logger.error(f"Error creating ticket category: {e}")
                await interaction.response.send_message(
                    "❌ Could not create ticket category. Please contact an admin.",
                    ephemeral=True
                )
                return
        
        # Create ticket channel
        ticket_name = f"ticket-{user.name}-{user.id}"
        
        try:
            ticket_channel = await guild.create_text_channel(
                name=ticket_name,
                category=category,
                overwrites=[
                    # Allow the user to read/write
                    discord.PermissionOverwrite(
                        user, read_messages=True, send_messages=True
                    ),
                    # Allow @everyone to read (but not write)
                    discord.PermissionOverwrite(
                        guild.default_role, read_messages=True, send_messages=False
                    ),
                    # Allow staff to read/write (will be updated when staff joins)
                    discord.PermissionOverwrite(
                        guild.default_role, read_messages=True, send_messages=True
                    )
                ],
                reason=f"Created ticket for {user.name}"
            )
            
            # Log ticket creation
            await self.database.log_ticket(
                user_id=user.id,
                username=user.name,
                guild_id=guild.id,
                channel_id=ticket_channel.id,
                staff_id=None
            )
            
            # Send welcome message
            welcome_embed = discord.Embed(
                title="🎟️ Support Ticket",
                description=f"Welcome {user.mention}! A staff member will assist you shortly.",
                color=discord.Color.blue()
            )
            welcome_embed.add_field(
                name="Ticket ID",
                value=str(ticket_channel.id),
                inline=True
            )
            welcome_embed.add_field(
                name="Status",
                value="Waiting for staff",
                inline=True
            )
            
            await ticket_channel.send(embed=welcome_embed)
            
            # Notify staff
            staff_embed = discord.Embed(
                title="🎟️ New Support Ticket",
                description=f"{user.mention} has opened a new ticket.",
                color=discord.Color.green()
            )
            staff_embed.add_field(
                name="User",
                value=f"{user.name} ({user.id})",
                inline=True
            )
            staff_embed.add_field(
                name="Channel",
                value=ticket_channel.mention,
                inline=True
            )
            
            # Send to staff channel if configured
            staff_channel = discord.utils.get(guild.text_channels, name="staff")
            if staff_channel:
                await staff_channel.send(embed=staff_embed)
            
            # Update the original button to reflect the ticket was created
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Ticket Created",
                custom_id="ticket_created",
                disabled=True
            ))
            
            await interaction.response.edit_message(view=view)
            
            logger.info(f"Ticket created for {user.name} (ID: {user.id}) in channel {ticket_channel.id}")
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message(
                "❌ Could not create ticket. Please try again.",
                ephemeral=True
            )
    
    async def close_ticket(self, interaction: Interaction):
        """Close a ticket."""
        # Implementation would depend on how you're identifying the ticket
        # This is a placeholder
        await interaction.response.send_message(
            "❌ Ticket closing is not yet implemented.",
            ephemeral=True
        )
    
    async def claim_ticket(self, interaction: Interaction):
        """Claim a ticket."""
        # Implementation would depend on how you're identifying the ticket
        # This is a placeholder
        await interaction.response.send_message(
            "❌ Ticket claiming is not yet implemented.",
            ephemeral=True
        )

class TicketView(discord.ui.View):
    def __init__(self, timeout=30):
        super().__init__(timeout=timeout)
        
        self.add_item(discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Create Support Ticket",
            custom_id="create_ticket",
            emoji="🎟️",
            description="Click to create a support ticket"
        ))
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
        bot = TicketBot(database)
        
        # Register slash commands
        @bot.tree.command(name="ticket", description="Open a support ticket")
        async def ticket_command(interaction: Interaction):
            """Slash command to open a ticket."""
            await interaction.response.send_message(
                "Please use the button below to create a support ticket.",
                embed=discord.Embed(
                    title="🎟️ Support Ticket",
                    description="Click the button below to create a support ticket.",
                    color=discord.Color.blue()
                ),
                view=TicketView()
            )
        
        @bot.tree.command(name="close", description="Close a ticket")
        async def close_command(interaction: Interaction):
            """Slash command to close a ticket."""
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Close Ticket",
                custom_id="close_ticket",
                emoji="🔒",
                description="Click to close this ticket"
            ))
            
            await interaction.response.send_message(
                "Are you sure you want to close this ticket?",
                view=view
            )
        
        @bot.tree.command(name="claim", description="Claim a ticket")
        async def claim_command(interaction: Interaction):
            """Slash command to claim a ticket."""
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Claim Ticket",
                custom_id="claim_ticket",
                emoji="✅",
                description="Click to claim this ticket"
            ))
            
            await interaction.response.send_message(
                "Are you sure you want to claim this ticket?",
                view=view
            )
        
        # Start the bot
        logger.info("Starting Discord Ticket Bot...")
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