import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY")
    DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET")
    DINGTALK_AGENT_ID = os.getenv("DINGTALK_AGENT_ID") # Added
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    DB_PATH = "bp_data.db"

    @classmethod
    def validate(cls):
        missing = []
        if not cls.DINGTALK_APP_KEY:
            missing.append("DINGTALK_APP_KEY")
        if not cls.DINGTALK_APP_SECRET:
            missing.append("DINGTALK_APP_SECRET")
        if not cls.DASHSCOPE_API_KEY:
            missing.append("DASHSCOPE_API_KEY")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
