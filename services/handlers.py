import logging
import json
from dingtalk_stream import AckMessage, CallbackHandler as BaseCallbackHandler
from services.database import DatabaseService
from services.image_analyzer import ImageAnalyzer
from services.dingtalk_api import DingTalkAPI

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.db = DatabaseService()
        self.dt_api = DingTalkAPI()

    def _format_time_to_cst(self, time_str):
        """
        Convert UTC time string to CST (UTC+8) string.
        Input format: YYYY-MM-DD HH:MM:SS
        """
        try:
            # Parse UTC time
            utc_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            # Add 8 hours
            cst_time = utc_time + timedelta(hours=8)
            # Format
            return cst_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(f"Error formatting time: {e}")
            return time_str

    def _calculate_bp_status(self, sys, dia):
        """
        Calculate blood pressure status based on systolic and diastolic values.
        Using Chinese hypertension guidelines.
        """
        try:
            sys = int(sys)
            dia = int(dia)
        except (ValueError, TypeError):
            return "未知"

        if sys >= 180 or dia >= 110:
            return "重度高血压 (请立即就医)"
        elif sys >= 160 or dia >= 100:
            return "中度高血压"
        elif sys >= 140 or dia >= 90:
            return "轻度高血压"
        elif sys >= 130 or dia >= 85:
            return "正常高值 (偏高)"
        elif sys >= 120 or dia >= 80:
            return "正常高值"
        else:
            return "正常血压"

    async def process(self, event):
        """
        Process incoming DingTalk events.
        """
        logger.info(f"Received event: {event}")
        if not event:
            logger.warning("Event is empty")
            return AckMessage.STATUS_OK, "ignored"
            
        # Debug: print event attributes
        try:
            logger.info(f"Event headers: {event.headers}")
            logger.info(f"Event data: {event.data}")
        except Exception as e:
            logger.error(f"Error printing event details: {e}")

        # Determine how to access data based on event type
        # The SDK might wrap it in different ways.
        # If event is CallbackMessage, it has .data (dict) and .headers
        
        data = event.data
        if not data:
             logger.warning("Event data is empty")
             return AckMessage.STATUS_OK, "empty data"

        msg_type = data.get("msgType") or data.get("msgtype")
        sender_id = data.get("senderStaffId", "")
        sender_nick = data.get("senderNick", "User")
        session_webhook = data.get("sessionWebhook")
        
        if not sender_id:
             return AckMessage.STATUS_OK, "no sender"

        # Text Message Handling
        if msg_type == "text":
            content = data.get("text", {}).get("content", "").strip()
            if content == "历史":
                return await self.handle_history(sender_id, session_webhook)
            else:
                await self.reply_text(sender_id, f"欢迎 {sender_nick}! 请发送血压计的照片给我，或者输入 '历史' 查看您的记录。", session_webhook)
                return AckMessage.STATUS_OK, "replied"

        # Image Message Handling
        elif msg_type == "picture":
            content_data = data.get("content", {})
            logger.info(f"Picture content data: {content_data}")
            download_code = content_data.get("downloadCode")
            
            if not download_code:
                # Fallback: maybe 'pictureDownloadUrl' exists in some contexts
                image_url = content_data.get("pictureDownloadUrl") # Legacy
            else:
                image_url = self.dt_api.get_file_download_url(download_code)

            if not image_url:
                await self.reply_text(sender_id, "抱歉，无法下载图片，请重试。", session_webhook)
                return AckMessage.STATUS_OK, "failed download"

            await self.reply_text(sender_id, "已收到图片，正在分析...", session_webhook)

            # Analyze
            result = ImageAnalyzer.analyze_bp_image(image_url)
            
            if "error" in result:
                await self.reply_text(sender_id, f"分析失败: {result['error']}", session_webhook)
            else:
                # Save to DB
                sys = result.get("systolic")
                dia = result.get("diastolic")
                pulse = result.get("pulse")
                
                bp_result = self._calculate_bp_status(sys, dia)
                
                self.db.add_record(sender_id, sender_nick, sys, dia, pulse, image_url, bp_result)
                
                msg = (f"**分析结果**\n\n"
                       f"收缩压 (高压): {sys}\n"
                       f"舒张压 (低压): {dia}\n"
                       f"脉搏: {pulse}\n"
                       f"结果: **{bp_result}**\n\n"
                       f"已保存到您的历史记录。")
                
                await self.reply_text(sender_id, msg, session_webhook, msg_type="markdown", title="血压分析结果")

        return AckMessage.STATUS_OK, "processed"

    async def reply_text(self, user_id, text, webhook_url=None, msg_type="text", title=None):
        success = self.dt_api.send_text_message(user_id, text, webhook_url, msg_type, title)
        if not success:
            logger.error(f"Failed to reply to user {user_id}")

    async def handle_history(self, user_id, webhook_url=None):
        records = self.db.get_user_history(user_id)
        if not records:
            response_text = "暂无记录。"
        else:
            lines = ["### 最近记录"]
            for r in records:
                # r = (sys, dias, pulse, time, url, result)
                # indices: 0:sys, 1:dia, 2:pulse, 3:time, 4:url, 5:result
                
                # Format time to CST
                time_str = self._format_time_to_cst(r[3])
                
                res_str = f" **{r[5]}**" if r[5] else ""
                lines.append(f"- {time_str}\n  - 高压: {r[0]} | 低压: {r[1]} | 脉搏: {r[2]}{res_str}")
            response_text = "\n".join(lines)
        
        await self.reply_text(user_id, response_text, webhook_url, msg_type="markdown", title="历史记录")
        return AckMessage.STATUS_OK, "history processed"
