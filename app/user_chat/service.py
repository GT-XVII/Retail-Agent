"""User chat service that coordinates history and the retail agent."""

from app.agent.retail_agent import RetailAgent
from app.errors import ChatServiceError, RetailAgentError
from app.user_chat.history import InMemoryChatHistoryStore
from app.user_chat.models import ChatRequest, ChatResponse


class UserChatService:
    """Handle chat requests and keep conversation history."""

    def __init__(self, agent_factory=None, history_store=None):
        self.agent_factory = agent_factory or RetailAgent
        self.history_store = history_store or InMemoryChatHistoryStore()
        self._agent = None

    def send_message(self, request):
        try:
            previous_history = self.history_store.get_messages(
                request.user_id,
                request.conversation_id,
            )
            previous_messages = [
                message.model_dump()
                for message in previous_history
            ]

            self.history_store.append_message(
                request.user_id,
                request.conversation_id,
                "user",
                request.message,
            )
            response_message = self._get_agent().run(
                request.message,
                history=previous_messages,
            )
            self.history_store.append_message(
                request.user_id,
                request.conversation_id,
                "assistant",
                response_message,
            )

            return ChatResponse(
                message=response_message,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                history=self.history_store.get_messages(
                    request.user_id,
                    request.conversation_id,
                ),
            )
        except RetailAgentError:
            raise
        except Exception as error:
            raise ChatServiceError(
                "Failed to process the chat message.",
                details={
                    "type": type(error).__name__,
                    "message": str(error),
                    "user_id": request.user_id,
                    "conversation_id": request.conversation_id,
                },
            ) from error

    def clear_history(self, user_id, conversation_id):
        self.history_store.clear(user_id, conversation_id)

    def _get_agent(self):
        try:
            if self._agent is None:
                self._agent = self.agent_factory()
        except RetailAgentError:
            raise
        except Exception as error:
            raise ChatServiceError(
                "Failed to create the retail chat agent.",
                details={
                    "type": type(error).__name__,
                    "message": str(error),
                },
            ) from error

        return self._agent
