import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Move mock setup AFTER imports that need real modules
from dotenv import load_dotenv
load_dotenv()

# Mock only DingTalk components, let DashScope/Requests be real
sys.modules["dingtalk_stream"] = MagicMock()
# sys.modules["sys.modules"] = MagicMock() # Don't mock sys

# Setup DingTalk Stream Mock values
sys.modules["dingtalk_stream"].AckMessage.STATUS_OK = 0
sys.modules["dingtalk_stream"].AckMessage.STATUS_FAIL = 1

from services.handlers import CallbackHandler
from config import Config

logging.basicConfig(level=logging.INFO)

async def test_flow():
    print("--- Starting Local Verification (Real Image Analysis) ---")
    
    # Check API Key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("ERROR: DASHSCOPE_API_KEY is missing in .env")
        return

    # Mock external dependencies (ONLY DingTalk API, NOT ImageAnalyzer)
    with patch('services.handlers.DingTalkAPI') as MockAPI:
        
        # Setup Mocks
        mock_api = MockAPI.return_value
        # Real image URL
        real_image_url = "https://cdnd.kexu.com/public/images/e8/82/af/7dd04d8f199a3ce4c89291d0f502b0b85b2253c1.jpg"
        mock_api.get_file_download_url.return_value = real_image_url
        mock_api.send_text_message.return_value = True
        
        # Initialize Handler
        handler = CallbackHandler()
        
        # 1. Test Image Message
        print(f"\n[Test] Testing Image Analysis for URL: {real_image_url}")
        image_event = MagicMock()
        image_event.type = "eventType"
        image_event.data = {
            "msgType": "picture",
            "senderStaffId": "user123",
            "senderNick": "Test User",
            "content": {"downloadCode": "fake_code_for_mock_api"}
        }
        
        # This will call the REAL ImageAnalyzer, which calls REAL DashScope
        await handler.process(image_event)
        
        # Verify DB insertion
        records = handler.db.get_user_history("user123")
        if records:
            latest = records[0]
            print(f"\n[Success] Analysis Result Saved to DB:")
            print(f"Time: {latest[3]}")
            print(f"Systolic: {latest[0]}")
            print(f"Diastolic: {latest[1]}")
            print(f"Pulse: {latest[2]}")
        else:
            print("\n[Failed] No records found in DB. Analysis might have failed.")
            
        print("\n--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(test_flow())
