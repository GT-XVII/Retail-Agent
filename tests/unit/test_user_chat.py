from app.user_chat.history import InMemoryChatHistoryStore
from app.errors import AgentExecutionError, ChatServiceError
from app.user_chat.models import ChatRequest
from app.user_chat.service import UserChatService


class FakeAgent:
    def __init__(self):
        self.calls = []

    def run(self, message, history=None):
        self.calls.append({"message": message, "history": history})

        return f"response to {message}"


class FailingHistoryStore:
    def get_messages(self, user_id, conversation_id):
        raise RuntimeError("history unavailable")

    def append_message(self, user_id, conversation_id, role, content):
        raise AssertionError("append should not be reached")

    def clear(self, user_id, conversation_id):
        pass


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


def test_user_chat_service_preserves_agent_errors():
    class FailingAgent:
        def run(self, message, history=None):
            raise AgentExecutionError("agent failed")

    service = UserChatService(agent_factory=FailingAgent)

    try:
        service.send_message(ChatRequest(message="hello"))
    except AgentExecutionError as error:
        assert error.message == "agent failed"


def test_user_chat_service_wraps_history_errors():
    service = UserChatService(
        agent_factory=FakeAgent,
        history_store=FailingHistoryStore(),
    )

    try:
        service.send_message(ChatRequest(message="hello"))
    except ChatServiceError as error:
        assert error.to_response()["error"]["details"]["message"] == "history unavailable"


def test_user_chat_service_wraps_agent_factory_errors():
    def fail_agent_factory():
        raise RuntimeError("factory unavailable")

    service = UserChatService(agent_factory=fail_agent_factory)

    try:
        service._get_agent()
    except ChatServiceError as error:
        assert error.to_response()["error"]["details"] == {
            "type": "RuntimeError",
            "message": "factory unavailable",
        }


def test_user_chat_service_preserves_agent_factory_retail_errors():
    error = AgentExecutionError("factory agent error")

    def fail_agent_factory():
        raise error

    service = UserChatService(agent_factory=fail_agent_factory)

    try:
        service._get_agent()
    except AgentExecutionError as raised:
        assert raised is error
