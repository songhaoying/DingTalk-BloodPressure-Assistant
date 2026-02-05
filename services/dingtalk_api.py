import requests
import json
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

class DingTalkAPI:
    def __init__(self):
        self.app_key = Config.DINGTALK_APP_KEY
        self.app_secret = Config.DINGTALK_APP_SECRET
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self):
        """
        Get logic to fetch or refresh access_token.
        """
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        try:
            resp = requests.get(url, params=params)
            data = resp.json()
            if data.get("errcode") == 0:
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data["expires_in"] - 60 # Buffer
                return self.access_token
            else:
                logger.error(f"Failed to get token: {data}")
                return None
        except Exception as e:
            logger.error(f"Error fetching token: {e}")
            return None

    def send_text_message(self, user_id, content, webhook_url=None, msg_type="text", title=None):
        """
        Send a message to a user.
        Supports text and markdown.
        
        Args:
            user_id: user id(s)
            content: text content or markdown content
            webhook_url: session webhook url
            msg_type: "text" or "markdown"
            title: title for markdown message
        """
        # Method 1: Session Webhook (Preferred for Chat Window Reply)
        if webhook_url:
            try:
                if msg_type == "markdown":
                    payload = {
                        "msgtype": "markdown",
                        "markdown": {
                            "title": title or "Message",
                            "text": content
                        }
                    }
                else:
                    payload = {
                        "msgtype": "text",
                        "text": {
                            "content": content
                        }
                    }
                    
                resp = requests.post(webhook_url, json=payload)
                if resp.status_code == 200:
                    return True
                else:
                    logger.error(f"Failed to send via webhook: {resp.text}")
            except Exception as e:
                logger.error(f"Error sending via webhook: {e}")

        # Method 2: Standard API (Fall back or if no webhook provided)
        token = self.get_access_token()
        if not token:
            return False

        url = "https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend"
        
        headers = {
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }
        
        # user_id can be a comma-separated string or a list
        if isinstance(user_id, str):
            user_ids = user_id.split(',')
        else:
            user_ids = user_id
        
        if msg_type == "markdown":
            msg_key = "sampleMarkdown"
            msg_param = json.dumps({"title": title or "Message", "text": content})
        else:
            msg_key = "sampleText"
            msg_param = json.dumps({"content": content})
            
        payload = {
            "robotCode": self.app_key,
            "userIds": user_ids,
            "msgKey": msg_key,
            "msgParam": msg_param
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload)
            data = resp.json()
            # v1.0 API usually returns request_id on success, or check status code
            if resp.status_code == 200:
                return True
            else:
                logger.error(f"Failed to send message: {data}")
                return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def _get_agent_id(self):
        # This should come from config
        return getattr(Config, 'DINGTALK_AGENT_ID', None)
        
    def get_file_download_url(self, download_code):
        """
        Get the download URL for a file using its download code.
        Using v1.0 API
        """
        token = self.get_access_token()
        if not token:
            return None
            
        url = "https://api.dingtalk.com/v1.0/robot/messageFiles/download"
        
        headers = {
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json"
        }
        
        data = {
            "downloadCode": download_code,
            "robotCode": self.app_key
        }
        
        try:
            resp = requests.post(url, headers=headers, json=data)
            res = resp.json()
            
            if resp.status_code == 200 and "downloadUrl" in res:
                return res.get("downloadUrl")
            else:
                logger.error(f"Failed to get download url. Status: {resp.status_code}, Response: {res}")
                return None
        except Exception as e:
            logger.error(f"Error getting download url: {e}")
            return None
