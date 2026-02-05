import sqlite3
import logging
import os
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.db_type = Config.DB_TYPE
        
        if self.db_type == "sqlserver":
            try:
                import pyodbc
                self.pyodbc = pyodbc
            except ImportError:
                logger.error("pyodbc is required for SQL Server but not installed.")
                raise
                
        self.db_path = Config.DB_PATH
        self._init_db()

    def _get_connection(self):
        if self.db_type == "sqlserver":
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={Config.SQLSERVER_HOST},{Config.SQLSERVER_PORT};"
                f"DATABASE={Config.SQLSERVER_DB};"
                f"UID={Config.SQLSERVER_USER};"
                f"PWD={Config.SQLSERVER_PASSWORD};"
                f"TrustServerCertificate=yes;"
                f"Encrypt=no;"  
            )
            return self.pyodbc.connect(conn_str)
        else:
            return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize the database schema."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if self.db_type == "sqlserver":
                # SQL Server Schema
                # Check if table exists
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='员工血压记录' AND xtype='U')
                    BEGIN
                        CREATE TABLE 员工血压记录 (
                            ID INT IDENTITY(1,1) PRIMARY KEY,
                            员工ID NVARCHAR(100) NOT NULL,
                            员工姓名 NVARCHAR(100),
                            收缩压 INT,
                            舒张压 INT,
                            脉搏 INT,
                            图片链接 NVARCHAR(MAX),
                            分析结果 NVARCHAR(MAX),
                            记录时间 DATETIME DEFAULT GETDATE()
                        )
                    END
                """)
            else:
                # SQLite Schema (Legacy)
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
            conn.close()
            logger.info(f"Database ({self.db_type}) initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def add_record(self, user_id, user_name, systolic, diastolic, pulse, image_url=None, result=None):
        """Add a new blood pressure record."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if self.db_type == "sqlserver":
                cursor.execute("""
                    INSERT INTO 员工血压记录 (员工ID, 员工姓名, 收缩压, 舒张压, 脉搏, 图片链接, 分析结果)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, user_name, systolic, diastolic, pulse, image_url, result))
                
                # Get last inserted ID
                cursor.execute("SELECT @@IDENTITY")
                last_id = cursor.fetchone()[0]
            else:
                cursor.execute("""
                    INSERT INTO records (user_id, user_name, systolic, diastolic, pulse, image_url, result)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, user_name, systolic, diastolic, pulse, image_url, result))
                last_id = cursor.lastrowid
                
            conn.commit()
            conn.close()
            return last_id
        except Exception as e:
            logger.error(f"Error adding record: {e}")
            return None

    def get_user_history(self, user_id, limit=10):
        """Get the last N records for a user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if self.db_type == "sqlserver":
                # Note: TOP is used in SQL Server instead of LIMIT
                cursor.execute("""
                    SELECT TOP (?) 收缩压, 舒张压, 脉搏, 记录时间, 图片链接, 分析结果
                    FROM 员工血压记录
                    WHERE 员工ID = ?
                    ORDER BY 记录时间 DESC
                """, (limit, user_id))
                
                # Convert pyodbc rows to tuples to match sqlite format if needed
                # pyodbc returns Row objects which are indexable like tuples
                rows = cursor.fetchall()
                
                # Format time string to match SQLite's string format if necessary
                # SQL Server returns datetime objects. SQLite returns strings (usually).
                # The handlers.py expects a string in _format_time_to_cst: datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                # So we need to convert datetime objects to string
                result_rows = []
                for row in rows:
                    # row indices: 0:sys, 1:dia, 2:pulse, 3:time, 4:url, 5:result
                    time_val = row[3]
                    if isinstance(time_val, datetime):
                        time_str = time_val.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        time_str = str(time_val)
                    
                    result_rows.append((row[0], row[1], row[2], time_str, row[4], row[5]))
                
                conn.close()
                return result_rows
            else:
                cursor.execute("""
                    SELECT systolic, diastolic, pulse, created_at, image_url, result
                    FROM records
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit))
                rows = cursor.fetchall()
                conn.close()
                return rows
                
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            return []
