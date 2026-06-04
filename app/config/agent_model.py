"""Agent model factory configuration."""

import os
from dataclasses import dataclass
from typing import Callable

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.errors import ModelConfigurationError

load_dotenv()


@dataclass(frozen=True)
class AgentModelConfig:
    provider: str
    model: str
    api_key: str | None
    base_url: str | None
    temperature: float


ModelFactory = Callable[[AgentModelConfig], object]


def get_agent_model_config(provider=None):
    """Read agent model settings from environment variables."""

    provider = (provider or os.getenv("AGENT_MODEL_PROVIDER", "airefinery")).lower()

    if provider == "airefinery":
        return _get_airefinery_config()

    if provider == "openai":
        return _get_openai_config()

    raise ModelConfigurationError(
        "Unsupported agent model provider.",
        details={"provider": provider},
    )


def _get_airefinery_config():
    """Read AI Refinery settings for its OpenAI-compatible chat API."""

    return AgentModelConfig(
        provider="airefinery",
        model=os.getenv("AIREFINERY_MODEL_NAME", "openai/gpt-oss-120b"),
        api_key=os.getenv("AIREFINERY_API_KEY"),
        base_url=os.getenv("AIREFINERY_BASE_URL"),
        temperature=float(os.getenv("AIREFINERY_TEMPERATURE", "0")),
    )


def _get_openai_config():
    """Read direct OpenAI settings."""

    return AgentModelConfig(
        provider="openai",
        model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0")),
    )


def create_openai_compatible_chat_model(config):
    """Create a ChatOpenAI model for OpenAI-compatible chat APIs."""

    if not config.api_key:
        raise ModelConfigurationError(
            "Missing API key for agent model provider.",
            details={
                "provider": config.provider,
                "expected_env": _provider_api_key_env(config.provider),
            },
        )

    return ChatOpenAI(
        model=config.model,
        api_key=config.api_key,
        base_url=config.base_url,
        temperature=config.temperature,
    )


MODEL_FACTORIES: dict[str, ModelFactory] = {
    "airefinery": create_openai_compatible_chat_model,
    "openai": create_openai_compatible_chat_model,
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


def _provider_api_key_env(provider):
    return {
        "airefinery": "AIREFINERY_API_KEY",
        "openai": "OPENAI_API_KEY",
    }.get(provider, "provider-specific API key environment variable")
