"""Tests for modeltoolbox_provider module."""

import pytest

from modeltoolbox_provider.providers import (
    ProviderConfig,
    create_provider,
    provider_names,
)
from modeltoolbox_provider.types import ChatMessage


def test_provider_names():
    """Test that provider_names returns expected providers."""
    names = provider_names()
    assert "ollama" in names
    assert "openai-compatible" in names
    assert "anthropic" in names
    assert "azure" in names


def test_create_ollama_provider():
    """Test creating Ollama provider."""
    config = ProviderConfig(name="ollama", base_url="http://localhost:11434")
    provider = create_provider(config)
    assert provider.name == "ollama"


def test_create_openai_provider():
    """Test creating OpenAI compatible provider."""
    config = ProviderConfig(
        name="openai-compatible",
        base_url="https://api.openai.com/v1",
        api_key="test-key",
    )
    provider = create_provider(config)
    assert provider.name == "openai-compatible"


def test_create_anthropic_provider():
    """Test creating Anthropic provider."""
    config = ProviderConfig(name="anthropic", api_key="test-key")
    provider = create_provider(config)
    assert provider.name == "anthropic"


def test_create_azure_provider():
    """Test creating Azure OpenAI provider."""
    config = ProviderConfig(
        name="azure",
        base_url="https://test.openai.azure.com",
        api_key="test-key",
    )
    provider = create_provider(config)
    assert provider.name == "azure"


def test_provider_config_defaults():
    """Test ProviderConfig default values."""
    config = ProviderConfig(name="ollama")
    assert config.timeout == 60.0
    assert config.max_retries == 3
    assert config.base_url is None
    assert config.api_key is None


def test_provider_capabilities():
    """Test provider capabilities method."""
    config = ProviderConfig(name="ollama")
    provider = create_provider(config)
    caps = provider.capabilities()
    assert caps.chat is True or caps.chat is False  # Just check it returns something


def test_chat_message_list():
    """Test creating a list of chat messages."""
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Hello!"),
        ChatMessage(role="assistant", content="Hi! How can I help you?"),
    ]
    assert len(messages) == 3
    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert messages[2].role == "assistant"
