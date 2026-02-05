from http import HTTPStatus
import dashscope
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

# Ensure API key is set
dashscope.api_key = Config.DASHSCOPE_API_KEY

class ImageAnalyzer:
    @staticmethod
    def analyze_bp_image(image_url):
        """
        Analyzes a blood pressure monitor image using Qwen-VL.
        Returns a dictionary with systolic, diastolic, and pulse values.
        """
        prompt = (
            "Please analyze this image of a blood pressure monitor. "
            "Extract the Systolic (High), Diastolic (Low), and Pulse (Heart Rate) numbers. "
            "Return the result ONLY as a JSON object with keys: 'systolic', 'diastolic', 'pulse'. "
            "If you cannot read the screen or it's not a BP monitor, return {'error': 'Cannot read image'}. "
            "Do not include markdown or explanations, just the JSON string."
        )
        
        # We need to use the qwen-vl-max or qwen-vl-plus model
        # Messages format for Qwen-VL
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": image_url},
                    {"text": prompt}
                ]
            }
        ]

        try:
            response = dashscope.MultiModalConversation.call(model='qwen-vl-max',
                                                             messages=messages)
            
            if response.status_code == HTTPStatus.OK:
                content = response.output.choices[0].message.content[0]['text']
                # Clean up potential markdown code blocks
                content = content.replace("```json", "").replace("```", "").strip()
                try:
                    data = json.loads(content)
                    return data
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from VL response: {content}")
                    return {"error": "Failed to parse data"}
            else:
                logger.error(f"DashScope API Error: {response.code} - {response.message}")
                return {"error": f"API Error: {response.message}"}
                
        except Exception as e:
            logger.error(f"Exception during image analysis: {e}")
            return {"error": "Internal error during analysis"}
