import pytest

from app.config import agent_model
from app.config.agent_model import AgentModelConfig
from app.errors import ModelConfigurationError


def test_get_agent_model_config_reads_custom_environment(monkeypatch):
    monkeypatch.setenv("AGENT_MODEL_PROVIDER", "custom")
    monkeypatch.setenv("MODEL_NAME", "private-model")
    monkeypatch.setenv("MODEL_API_KEY", "private-key")
    monkeypatch.setenv("MODEL_TEMPERATURE", "0.2")
    monkeypatch.setenv("MODEL_FACTORY_MODULE", "private.module")
    monkeypatch.setenv("MODEL_FACTORY_FUNCTION", "build_model")

    config = agent_model.get_agent_model_config()

    assert config == AgentModelConfig(
        provider="custom",
        model="private-model",
        api_key="private-key",
        temperature=0.2,
        factory_module="private.module",
        factory_function="build_model",
    )


def test_get_agent_model_config_defaults_to_custom(monkeypatch):
    monkeypatch.delenv("AGENT_MODEL_PROVIDER", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_TEMPERATURE", raising=False)
    monkeypatch.delenv("MODEL_FACTORY_MODULE", raising=False)
    monkeypatch.delenv("MODEL_FACTORY_FUNCTION", raising=False)

    config = agent_model.get_agent_model_config()

    assert config == AgentModelConfig(
        provider="custom",
        model="your-model-name",
        api_key=None,
        temperature=0,
        factory_module="app.config.local_chat_model",
        factory_function="create_chat_model",
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


def test_create_chat_model_uses_registered_provider_factory(monkeypatch):
    created = {}

    def fake_factory(config):
        created["config"] = config

        return "fake-model"

    monkeypatch.setitem(agent_model.MODEL_FACTORIES, "test-provider", fake_factory)

    config = AgentModelConfig(
        provider="test-provider",
        model="private-model",
        api_key="secret",
        temperature=0.3,
        factory_module="private.module",
        factory_function="build_model",
    )

    assert agent_model.create_chat_model(config) == "fake-model"
    assert created["config"] == config


def test_create_chat_model_rejects_unknown_provider():
    config = AgentModelConfig(
        provider="unknown",
        model="private-model",
        api_key="secret",
        temperature=0.3,
        factory_module="private.module",
        factory_function="build_model",
    )

    with pytest.raises(ModelConfigurationError) as error:
        agent_model.create_chat_model(config)

    assert error.value.details == {"provider": "unknown"}


def test_create_custom_chat_model_requires_api_key():
    config = AgentModelConfig(
        provider="custom",
        model="private-model",
        api_key=None,
        temperature=0.3,
        factory_module="private.module",
        factory_function="build_model",
    )

    with pytest.raises(ModelConfigurationError) as error:
        agent_model.create_custom_chat_model(config)

    assert error.value.to_response()["error"]["details"] == {
        "provider": "custom",
        "expected_env": "MODEL_API_KEY",
    }


def test_create_custom_chat_model_loads_configured_factory(monkeypatch):
    created = {}

    class FakeModule:
        @staticmethod
        def build_model(config):
            created["config"] = config

            return "private-model-instance"

    monkeypatch.setattr(
        agent_model.importlib,
        "import_module",
        lambda module_name: FakeModule,
    )

    config = AgentModelConfig(
        provider="custom",
        model="private-model",
        api_key="secret",
        temperature=0.3,
        factory_module="private.module",
        factory_function="build_model",
    )

    assert agent_model.create_custom_chat_model(config) == "private-model-instance"
    assert created["config"] == config


def test_create_custom_chat_model_wraps_factory_import_errors(monkeypatch):
    def fail_import(module_name):
        raise ImportError("missing private module")

    monkeypatch.setattr(agent_model.importlib, "import_module", fail_import)

    config = AgentModelConfig(
        provider="custom",
        model="private-model",
        api_key="secret",
        temperature=0.3,
        factory_module="private.module",
        factory_function="build_model",
    )

    with pytest.raises(ModelConfigurationError) as error:
        agent_model.create_custom_chat_model(config)

    assert error.value.to_response()["error"]["details"] == {
        "provider": "custom",
        "factory_module": "private.module",
        "factory_function": "build_model",
        "type": "ImportError",
        "message": "missing private module",
    }


def test_create_custom_chat_model_wraps_missing_factory_function(monkeypatch):
    class FakeModule:
        pass

    monkeypatch.setattr(
        agent_model.importlib,
        "import_module",
        lambda module_name: FakeModule,
    )

    config = AgentModelConfig(
        provider="custom",
        model="private-model",
        api_key="secret",
        temperature=0.3,
        factory_module="private.module",
        factory_function="build_model",
    )

    with pytest.raises(ModelConfigurationError) as error:
        agent_model.create_custom_chat_model(config)

    assert error.value.to_response()["error"]["details"]["type"] == "AttributeError"
