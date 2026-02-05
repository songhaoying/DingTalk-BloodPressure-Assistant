import sqlite3
import os
import sys
import logging
from config import Config
from services.database import DatabaseService

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate():
    """
    Migrate data from SQLite to SQL Server.
    Assumes Config is set up for SQL Server, but we need to manually access SQLite.
    """
    
    # Check if we are configured for SQL Server
    if Config.DB_TYPE != "sqlserver":
        logger.error("Error: DB_TYPE in .env must be set to 'sqlserver' for migration destination.")
        logger.info("Please update .env and try again.")
        return

    # Check if SQLite DB exists
    sqlite_path = Config.DB_PATH
    if not os.path.exists(sqlite_path):
        logger.error(f"Error: SQLite database file not found at {sqlite_path}")
        return

    logger.info("Starting migration from SQLite to SQL Server...")
    
    # Initialize SQL Server connection via DatabaseService
    try:
        db_service = DatabaseService()
        # This initializes the table if it doesn't exist
    except Exception as e:
        logger.error(f"Failed to connect to SQL Server: {e}")
        return

    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Read all records from SQLite
        sqlite_cursor.execute("SELECT user_id, user_name, systolic, diastolic, pulse, image_url, result, created_at FROM records")
        records = sqlite_cursor.fetchall()
        logger.info(f"Found {len(records)} records in SQLite database.")
        
        sqlite_conn.close()
    except Exception as e:
        logger.error(f"Error reading from SQLite: {e}")
        return

    # Insert into SQL Server
    success_count = 0
    fail_count = 0
    
    conn = db_service._get_connection()
    cursor = conn.cursor()
    
    for r in records:
        # r: user_id, user_name, sys, dia, pulse, url, result, created_at
        try:
            # Check if record already exists (optional, simple check by time and user)
            # Or just insert blindly assuming empty target table
            
            cursor.execute("""
                INSERT INTO 员工血压记录 (员工ID, 员工姓名, 收缩压, 舒张压, 脉搏, 图片链接, 分析结果, 记录时间)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to insert record for user {r[0]}: {e}")
            fail_count += 1
            
    try:
        conn.commit()
        conn.close()
        logger.info(f"Migration complete. Success: {success_count}, Failed: {fail_count}")
    except Exception as e:
        logger.error(f"Error committing transaction: {e}")

if __name__ == "__main__":
    # Ensure pyodbc is installed
    try:
        import pyodbc
    except ImportError:
        print("Error: pyodbc is not installed. Please run: pip install pyodbc")
        sys.exit(1)
        
    migrate()
