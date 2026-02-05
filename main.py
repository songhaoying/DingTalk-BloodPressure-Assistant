import asyncio
import logging
from dingtalk_stream import DingTalkStreamClient, AckMessage, Credential
from dingtalk_stream.chatbot import ChatbotMessage
from config import Config
from services.handlers import CallbackHandler

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Load and validate config
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        return

    # Initialize Client
    credential = Credential(Config.DINGTALK_APP_KEY, Config.DINGTALK_APP_SECRET)
    client = DingTalkStreamClient(credential)

    # Initialize Handlers
    # We need to pass the client to the handler so it can send replies
    handler = CallbackHandler()
    
    # Monkey patch or set the client on the handler if we improve the handler class
    # handler.client = client 
    # But wait, `DingTalkStreamClient` is for receiving. sending usually requires the HTTP api.
    # The `dingtalk_stream` library might have a method to register callback.

    async def on_event(event):
        try:
            # We need to adapt the handler to what the library expects
            # The library likely calls this with an event object
            return await handler.process(event)
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return AckMessage.STATUS_FAIL, f"Error: {e}"

    # Register callback
    # The register_callback_handler expects a handler object, not a function
    # But our handler.process is the logic we want. 
    # The SDK expects an object that has 'pre_start' and 'process' methods.
    # Our CallbackHandler now inherits from the SDK's CallbackHandler.
    
    # We should register the handler instance itself, not the on_event wrapper function.
    # But wait, our handler logic might differ from what SDK expects in process().
    
    # Let's check SDK's CallbackHandler.process signature: async def process(self, message: CallbackMessage)
    # Our handler.process(event) matches this if 'event' is a CallbackMessage.
    
    # So we should register the handler instance directly.
    client.register_callback_handler(ChatbotMessage.TOPIC, handler)

    logger.info("Starting DingTalk Stream Client...")
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
