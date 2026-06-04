from app.user_chat.history import InMemoryChatHistoryStore
from app.user_chat.models import ChatRequest
from app.user_chat.service import UserChatService


class FakeAgent:
    def __init__(self):
        self.calls = []

    def run(self, message, history=None):
        self.calls.append({"message": message, "history": history})

        return f"response to {message}"


def test_in_memory_chat_history_store_keeps_messages_by_user_and_conversation():
    store = InMemoryChatHistoryStore()

    store.append_message("user-1", "conversation-1", "user", "hello")
    store.append_message("user-1", "conversation-1", "assistant", "hi")
    store.append_message("user-1", "conversation-2", "user", "other")

    assert [message.model_dump() for message in store.get_messages("user-1", "conversation-1")] == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    assert [message.model_dump() for message in store.get_messages("user-1", "conversation-2")] == [
        {"role": "user", "content": "other"},
    ]

    store.clear("user-1", "conversation-1")

    assert store.get_messages("user-1", "conversation-1") == []


def test_user_chat_service_sends_message_and_records_history():
    fake_agent = FakeAgent()
    service = UserChatService(agent_factory=lambda: fake_agent)

    first_response = service.send_message(
        ChatRequest(
            message="find a keyboard",
            user_id="user-1",
            conversation_id="conversation-1",
        )
    )
    second_response = service.send_message(
        ChatRequest(
            message="add it to cart",
            user_id="user-1",
            conversation_id="conversation-1",
        )
    )

    assert first_response.message == "response to find a keyboard"
    assert [message.model_dump() for message in first_response.history] == [
        {"role": "user", "content": "find a keyboard"},
        {"role": "assistant", "content": "response to find a keyboard"},
    ]
    assert fake_agent.calls == [
        {
            "message": "find a keyboard",
            "history": [],
        },
        {
            "message": "add it to cart",
            "history": [
                {"role": "user", "content": "find a keyboard"},
                {"role": "assistant", "content": "response to find a keyboard"},
            ],
        },
    ]
    assert [message.model_dump() for message in second_response.history] == [
        {"role": "user", "content": "find a keyboard"},
        {"role": "assistant", "content": "response to find a keyboard"},
        {"role": "user", "content": "add it to cart"},
        {"role": "assistant", "content": "response to add it to cart"},
    ]


def test_user_chat_service_clear_history():
    service = UserChatService(agent_factory=FakeAgent)
    request = ChatRequest(message="hello")

    service.send_message(request)
    service.clear_history(request.user_id, request.conversation_id)

    assert service.history_store.get_messages(request.user_id, request.conversation_id) == []
