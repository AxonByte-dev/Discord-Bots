"""
Database helper functions for the Discord Ticket Bot.
Uses SQLite with WAL mode for zero-latency, file-based data storage.
"""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
class Database:
    """Database helper class for managing SQLite connections and queries."""
    
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection with WAL mode."""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30
                )
                
                # Enable WAL mode for better performance and concurrency
                self._connection.execute("PRAGMA journal_mode = WAL")
                self._connection.execute("PRAGMA synchronous = NORMAL")
                self._connection.execute("PRAGMA cache_size = -2000")  # 2MB cache
                self._connection.execute("PRAGMA temp_store = MEMORY")
                
                logger.info(f"Database connection established: {self.db_path}")
                
            except sqlite3.Error as e:
                logger.error(f"Error connecting to database: {e}")
                raise
        
        return self._connection
    
    def close(self):
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    async def init_database(self):
        """Initialize the database with required tables."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create tickets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL UNIQUE,
                    staff_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP,
                    status TEXT DEFAULT 'open',
                    UNIQUE(channel_id)
                )
            """)
            
            # Create users table for user-specific data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    discriminator TEXT NOT NULL,
                    avatar TEXT,
                    ticket_count INTEGER DEFAULT 0,
                    last_ticket_at TIMESTAMP,
                    PRIMARY KEY (id)
                )
            """)
            
            # Create guilds table for guild-specific data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guilds (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ticket_category_id INTEGER,
                    staff_channel_id INTEGER,
                    welcome_message TEXT,
                    PRIMARY KEY (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_guild_id ON tickets(guild_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at)")
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor with automatic commit/rollback."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    async def log_ticket(
        self,
        user_id: int,
        username: str,
        guild_id: int,
        channel_id: int,
        staff_id: Optional[int] = None
    ):
        """Log a new ticket in the database."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT OR REPLACE INTO tickets 
                    (user_id, username, guild_id, channel_id, staff_id, status)
                    VALUES (?, ?, ?, ?, ?, 'open')
                """, (user_id, username, guild_id, channel_id, staff_id))
                
                # Update user ticket count
                cursor.execute("""
                    INSERT OR REPLACE INTO users
                    (id, username, discriminator, ticket_count, last_ticket_at)
                    VALUES (
                        ?, ?, ?, 
                        (SELECT COUNT(*) FROM tickets WHERE user_id = ?),
                        CURRENT_TIMESTAMP
                    )
                """, (user_id, username.split('#')[0], username.split('#')[1], user_id))
                
            logger.info(f"Ticket logged: user_id={user_id}, channel_id={channel_id}")
            
        except sqlite3.Error as e:
            logger.error(f"Error logging ticket: {e}")
            raise
    
    async def close_ticket(self, channel_id: int):
        """Mark a ticket as closed."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE tickets 
                    SET status = 'closed', closed_at = CURRENT_TIMESTAMP
                    WHERE channel_id = ?
                """, (channel_id,))
                
            logger.info(f"Ticket closed: channel_id={channel_id}")
            
        except sqlite3.Error as e:
            logger.error(f"Error closing ticket: {e}")
            raise
    
    async def claim_ticket(self, channel_id: int, staff_id: int):
        """Assign a staff member to a ticket."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE tickets 
                    SET staff_id = ?
                    WHERE channel_id = ? AND status = 'open'
                """, (staff_id, channel_id))
                
            logger.info(f"Ticket claimed: channel_id={channel_id}, staff_id={staff_id}")
            
        except sqlite3.Error as e:
            logger.error(f"Error claiming ticket: {e}")
            raise
    
    async def get_ticket(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """Get ticket information by channel ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM tickets WHERE channel_id = ?
                """, (channel_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                else:
                    return None
                    
        except sqlite3.Error as e:
            logger.error(f"Error getting ticket: {e}")
            raise
    
    async def get_user_tickets(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all tickets for a user."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC
                """, (user_id,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting user tickets: {e}")
            raise
    
    async def get_guild_tickets(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all tickets for a guild."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM tickets WHERE guild_id = ? ORDER BY created_at DESC
                """, (guild_id,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting guild tickets: {e}")
            raise
    
    async def get_open_tickets(self) -> List[Dict[str, Any]]:
        """Get all open tickets."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM tickets WHERE status = 'open' ORDER BY created_at ASC
                """)
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting open tickets: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self.get_cursor() as cursor:
                # Get total tickets count
                cursor.execute("SELECT COUNT(*) FROM tickets")
                total_tickets = cursor.fetchone()[0]
                
                # Get open tickets count
                cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
                open_tickets = cursor.fetchone()[0]
                
                # Get closed tickets count
                cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'")
                closed_tickets = cursor.fetchone()[0]
                
                # Get unique users with tickets
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM tickets")
                unique_users = cursor.fetchone()[0]
                
                return {
                    "total_tickets": total_tickets,
                    "open_tickets": open_tickets,
                    "closed_tickets": closed_tickets,
                    "unique_users": unique_users
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting stats: {e}")
            raise

# Global database instance
database_instance: Optional[Database] = None

def get_database() -> Database:
    """Get the global database instance."""
    global database_instance
    if database_instance is None:
        database_instance = Database()
    return database_instance
async def cleanup_database():
    """Clean up database resources."""
    global database_instance
    if database_instance is not None:
        database_instance.close()
        database_instance = None