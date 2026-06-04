import pytest

from app.errors import ModelConfigurationError
from app.config import agent_model
from app.config.agent_model import AgentModelConfig


def test_get_agent_model_config_reads_airefinery_environment(monkeypatch):
    monkeypatch.setenv("AGENT_MODEL_PROVIDER", "airefinery")
    monkeypatch.setenv("AIREFINERY_MODEL_NAME", "openai/gpt-oss-120b")
    monkeypatch.setenv("AIREFINERY_API_KEY", "airefinery-key")
    monkeypatch.setenv("AIREFINERY_BASE_URL", "https://airefinery.example.test")
    monkeypatch.setenv("AIREFINERY_TEMPERATURE", "0.2")

    config = agent_model.get_agent_model_config()

    assert config == AgentModelConfig(
        provider="airefinery",
        model="openai/gpt-oss-120b",
        api_key="airefinery-key",
        base_url="https://airefinery.example.test",
        temperature=0.2,
    )


def test_get_agent_model_config_reads_openai_environment(monkeypatch):
    monkeypatch.setenv("AGENT_MODEL_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://openai-compatible.example.test")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.4")

    config = agent_model.get_agent_model_config()

    assert config == AgentModelConfig(
        provider="openai",
        model="gpt-4o-mini",
        api_key="openai-key",
        base_url="https://openai-compatible.example.test",
        temperature=0.4,
    )


def test_get_agent_model_config_defaults_to_airefinery(monkeypatch):
    monkeypatch.delenv("AGENT_MODEL_PROVIDER", raising=False)
    monkeypatch.delenv("AIREFINERY_MODEL_NAME", raising=False)
    monkeypatch.delenv("AIREFINERY_API_KEY", raising=False)
    monkeypatch.delenv("AIREFINERY_BASE_URL", raising=False)
    monkeypatch.delenv("AIREFINERY_TEMPERATURE", raising=False)

    config = agent_model.get_agent_model_config()

    assert config == AgentModelConfig(
        provider="airefinery",
        model="openai/gpt-oss-120b",
        api_key=None,
        base_url=None,
        temperature=0,
    )


def test_get_agent_model_config_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("AGENT_MODEL_PROVIDER", "unknown")

    with pytest.raises(ModelConfigurationError) as error:
        agent_model.get_agent_model_config()

    assert error.value.to_response() == {
        "error": {
            "code": "model_configuration_error",
            "message": "Unsupported agent model provider.",
            "details": {"provider": "unknown"},
        }
    }


def test_create_chat_model_uses_provider_factory(monkeypatch):
    created = {}

    def fake_factory(config):
        created["config"] = config

        return "fake-model"

    monkeypatch.setitem(agent_model.MODEL_FACTORIES, "test-provider", fake_factory)

    config = AgentModelConfig(
        provider="test-provider",
        model="retail-model",
        api_key="secret",
        base_url="https://example.test",
        temperature=0.3,
    )

    assert agent_model.create_chat_model(config) == "fake-model"
    assert created["config"] == config


def test_create_chat_model_rejects_unknown_provider():
    config = AgentModelConfig(
        provider="unknown",
        model="retail-model",
        api_key="secret",
        base_url="https://example.test",
        temperature=0.3,
    )

    with pytest.raises(ModelConfigurationError) as error:
        agent_model.create_chat_model(config)

    assert error.value.details == {"provider": "unknown"}


def test_create_openai_compatible_chat_model_requires_api_key():
    config = AgentModelConfig(
        provider="airefinery",
        model="openai/gpt-oss-120b",
        api_key=None,
        base_url="https://example.test",
        temperature=0.3,
    )

    with pytest.raises(ModelConfigurationError) as error:
        agent_model.create_openai_compatible_chat_model(config)

    assert error.value.to_response()["error"]["details"] == {
        "provider": "airefinery",
        "expected_env": "AIREFINERY_API_KEY",
    }


def test_create_openai_compatible_chat_model_uses_config(monkeypatch):
    created = {}

    class FakeChatOpenAI:
        def __init__(self, model, api_key, base_url, temperature):
            created["model"] = model
            created["api_key"] = api_key
            created["base_url"] = base_url
            created["temperature"] = temperature

    monkeypatch.setattr(agent_model, "ChatOpenAI", FakeChatOpenAI)

    model = agent_model.create_openai_compatible_chat_model(
        AgentModelConfig(
            provider="airefinery",
            model="openai/gpt-oss-120b",
            api_key="secret",
            base_url="https://example.test",
            temperature=0.3,
        )
    )

    assert isinstance(model, FakeChatOpenAI)
    assert created == {
        "model": "openai/gpt-oss-120b",
        "api_key": "secret",
        "base_url": "https://example.test",
        "temperature": 0.3,
    }
