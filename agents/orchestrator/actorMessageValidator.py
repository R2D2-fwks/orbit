from chain.baseHandler import BaseHandler
from thespian.actors import ActorExitRequest,ChildActorExited, PoisonMessage,WakeupMessage,DeadEnvelope,ActorSystemConventionUpdate
from loguru import logger
class ActorMessageValidator(BaseHandler):
    def handle(self, context):
        message, orchestrator_self = context
        if(isinstance(message,(ActorExitRequest, ChildActorExited, PoisonMessage, WakeupMessage, DeadEnvelope, ActorSystemConventionUpdate))):
            # do action when the message is recived from the actor
            logger.info("[ActorMessageValidator] Received system message: {}", message)
            return context
        return super().handle(context)