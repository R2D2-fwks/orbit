from asyncio.log import logger
import json
from chain.baseHandler import BaseHandler
from messages.llm_message import LLMMessage

class LLMResponseValidator(BaseHandler):
    def handle(self, context):
        message,orchestrator_self,sender = context
        if isinstance(message,LLMMessage):
            msg = message.message
            return msg
        return super().handle(context)