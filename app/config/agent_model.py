"""Agent model factory configuration."""

import importlib
import os
from dataclasses import dataclass
from typing import Callable

from dotenv import load_dotenv

from app.errors import ModelConfigurationError

load_dotenv()


@dataclass(frozen=True)
class AgentModelConfig:
    provider: str
    model: str
    api_key: str | None
    temperature: float
    factory_module: str
    factory_function: str


ModelFactory = Callable[[AgentModelConfig], object]


def get_agent_model_config(provider=None):
    """Read agent model settings from environment variables."""

    provider = (provider or os.getenv("AGENT_MODEL_PROVIDER", "custom")).lower()

    if provider == "custom":
        return _get_custom_model_config()

    raise ModelConfigurationError(
        "Unsupported agent model provider.",
        details={"provider": provider},
    )


def _get_custom_model_config():
    """Read private/custom model provider settings."""

    return AgentModelConfig(
        provider="custom",
        model=os.getenv("MODEL_NAME", "your-model-name"),
        api_key=os.getenv("MODEL_API_KEY"),
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0")),
        factory_module=os.getenv(
            "MODEL_FACTORY_MODULE",
            "app.config.local_chat_model",
        ),
        factory_function=os.getenv(
            "MODEL_FACTORY_FUNCTION",
            "create_chat_model",
        ),
    )


def create_custom_chat_model(config):
    """Create a LangChain chat model from a private provider factory."""

    if not config.api_key:
        raise ModelConfigurationError(
            "Missing API key for agent model provider.",
            details={
                "provider": config.provider,
                "expected_env": "MODEL_API_KEY",
            },
        )

    try:
        module = importlib.import_module(config.factory_module)
        factory = getattr(module, config.factory_function)
    except (ImportError, AttributeError) as error:
        raise ModelConfigurationError(
            "Could not load the configured model factory.",
            details={
                "provider": config.provider,
                "factory_module": config.factory_module,
                "factory_function": config.factory_function,
                "type": type(error).__name__,
                "message": str(error),
            },
        ) from error

    return factory(config)


MODEL_FACTORIES: dict[str, ModelFactory] = {
    "custom": create_custom_chat_model,
}


def create_chat_model(config=None):
    """Create the LangChain chat model used by the retail agent."""

    config = config or get_agent_model_config()
    factory = MODEL_FACTORIES.get(config.provider)

    if factory is None:
        raise ModelConfigurationError(
            "Unsupported agent model provider.",
            details={"provider": config.provider},
        )

    return factory(config)
