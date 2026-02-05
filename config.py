import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY")
    DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET")
    DINGTALK_AGENT_ID = os.getenv("DINGTALK_AGENT_ID") # Added
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    # Database Config
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DB_PATH = "bp_data.db"
    
    # SQL Server Config
    SQLSERVER_HOST = os.getenv("SQLSERVER_HOST")
    SQLSERVER_PORT = os.getenv("SQLSERVER_PORT", "1433")
    SQLSERVER_USER = os.getenv("SQLSERVER_USER")
    SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD")
    SQLSERVER_DB = os.getenv("SQLSERVER_DB")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.DINGTALK_APP_KEY:
            missing.append("DINGTALK_APP_KEY")
        if not cls.DINGTALK_APP_SECRET:
            missing.append("DINGTALK_APP_SECRET")
        if not cls.DASHSCOPE_API_KEY:
            missing.append("DASHSCOPE_API_KEY")
            
        if cls.DB_TYPE == "sqlserver":
            if not cls.SQLSERVER_HOST: missing.append("SQLSERVER_HOST")
            if not cls.SQLSERVER_USER: missing.append("SQLSERVER_USER")
            if not cls.SQLSERVER_PASSWORD: missing.append("SQLSERVER_PASSWORD")
            if not cls.SQLSERVER_DB: missing.append("SQLSERVER_DB")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
