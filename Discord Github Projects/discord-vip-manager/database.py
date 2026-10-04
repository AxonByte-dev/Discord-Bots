"""
Database helper functions for the Discord VIP Manager Bot.
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
            
            # Create gift_codes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gift_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    gift_code TEXT NOT NULL UNIQUE,
                    status TEXT DEFAULT 'pending',
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    rejected_by INTEGER,
                    rejected_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (approved_by) REFERENCES users(id),
                    FOREIGN KEY (rejected_by) REFERENCES users(id)
                )
            """)
            
            # Create users table for user-specific data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    discriminator TEXT NOT NULL,
                    avatar TEXT,
                    role_granted_at TIMESTAMP,
                    PRIMARY KEY (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gift_codes_code ON gift_codes(gift_code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gift_codes_user_id ON gift_codes(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gift_codes_status ON gift_codes(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gift_codes_created_at ON gift_codes(created_at)")
            
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
    
    async def log_gift_code(
        self,
        user_id: int,
        username: str,
        gift_code: str,
        status: str = 'pending'
    ):
        """Log a new gift code submission."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    INSERT OR REPLACE INTO gift_codes 
                    (user_id, username, gift_code, status)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, gift_code, status))
                
            logger.info(f"Gift code logged: user_id={user_id}, code={gift_code}, status={status}")
            
        except sqlite3.Error as e:
            logger.error(f"Error logging gift code: {e}")
            raise
    
    async def update_gift_code_status(
        self,
        gift_code: str,
        status: str,
        moderator_id: int,
        moderator_action: str = 'approved' if status == 'approved' else 'rejected'
    ):
        """Update a gift code's status (approve or reject)."""
        try:
            with self.get_cursor() as cursor:
                if status == 'approved':
                    cursor.execute("""
                        UPDATE gift_codes 
                        SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
                        WHERE gift_code = ?
                    """, (status, moderator_id, gift_code))
                else:  # rejected
                    cursor.execute("""
                        UPDATE gift_codes 
                        SET status = ?, rejected_by = ?, rejected_at = CURRENT_TIMESTAMP
                        WHERE gift_code = ?
                    """, (status, moderator_id, gift_code))
                
            logger.info(f"Gift code updated: code={gift_code}, status={status}, moderator={moderator_id}")
            
        except sqlite3.Error as e:
            logger.error(f"Error updating gift code status: {e}")
            raise
    
    async def get_pending_gift_codes(self) -> List[Dict[str, Any]]:
        """Get all pending gift codes."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM gift_codes WHERE status = 'pending' ORDER BY created_at ASC
                """)
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting pending gift codes: {e}")
            raise
    
    async def get_gift_code_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get gift code submission history."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM gift_codes ORDER BY created_at DESC LIMIT ?
                """, (limit,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting gift code history: {e}")
            raise
    
    async def get_gift_code_stats(self) -> Dict[str, Any]:
        """Get database statistics for gift codes."""
        try:
            with self.get_cursor() as cursor:
                # Get total gift codes count
                cursor.execute("SELECT COUNT(*) FROM gift_codes")
                total_codes = cursor.fetchone()[0]
                
                # Get pending gift codes count
                cursor.execute("SELECT COUNT(*) FROM gift_codes WHERE status = 'pending'")
                pending_codes = cursor.fetchone()[0]
                
                # Get approved gift codes count
                cursor.execute("SELECT COUNT(*) FROM gift_codes WHERE status = 'approved'")
                approved_codes = cursor.fetchone()[0]
                
                # Get rejected gift codes count
                cursor.execute("SELECT COUNT(*) FROM gift_codes WHERE status = 'rejected'")
                rejected_codes = cursor.fetchone()[0]
                
                # Get unique users who submitted codes
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM gift_codes")
                unique_users = cursor.fetchone()[0]
                
                return {
                    "total_codes": total_codes,
                    "pending_codes": pending_codes,
                    "approved_codes": approved_codes,
                    "rejected_codes": rejected_codes,
                    "unique_users": unique_users
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting gift code stats: {e}")
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