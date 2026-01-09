from asyncio.log import logger
import json
from src.chain.baseHandler import BaseHandler
from src.messages.llm_message import LLMMessage

class LLMResponseValidator(BaseHandler):
    def handle(self, context):
        message,orchestrator_self,sender = context
        if isinstance(message,LLMMessage):
            msg = message.message
            return msg
        return super().handle(context)