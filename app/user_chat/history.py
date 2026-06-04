"""Chat history storage abstractions."""

from collections import defaultdict

from app.user_chat.models import ChatMessage


class InMemoryChatHistoryStore:
    """Store chat history in memory behind a replaceable interface."""

    def __init__(self):
        self._messages = defaultdict(list)

    def get_messages(self, user_id, conversation_id):
        return list(self._messages[self._key(user_id, conversation_id)])

    def append_message(self, user_id, conversation_id, role, content):
        message = ChatMessage(role=role, content=content)
        self._messages[self._key(user_id, conversation_id)].append(message)

        return message

    def clear(self, user_id, conversation_id):
        self._messages.pop(self._key(user_id, conversation_id), None)

    def _key(self, user_id, conversation_id):
        return (user_id, conversation_id)
