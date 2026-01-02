import json
from chain.baseHandler import BaseHandler
from messages.llm_message import LLMMessage

class LLMResponseValidator(BaseHandler):
    def handle(self, context):
        message,orchestrator_self = context
        if isinstance(message,LLMMessage):
            msg = message.message
            res = json.loads(msg.text)
            return res["response"]
        return super().handle(context)
        
    