import sqlite3
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize the database schema."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        user_name TEXT,
                        systolic INTEGER,
                        diastolic INTEGER,
                        pulse INTEGER,
                        image_url TEXT,
                        result TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Check if 'result' column exists (migration for existing dbs)
                cursor.execute("PRAGMA table_info(records)")
                columns = [info[1] for info in cursor.fetchall()]
                if "result" not in columns:
                    logger.info("Adding 'result' column to records table...")
                    cursor.execute("ALTER TABLE records ADD COLUMN result TEXT")
                
                conn.commit()
                logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def add_record(self, user_id, user_name, systolic, diastolic, pulse, image_url=None, result=None):
        """Add a new blood pressure record."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO records (user_id, user_name, systolic, diastolic, pulse, image_url, result)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, user_name, systolic, diastolic, pulse, image_url, result))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding record: {e}")
            return None

    def get_user_history(self, user_id, limit=10):
        """Get the last N records for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT systolic, diastolic, pulse, created_at, image_url, result
                    FROM records
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            return []
