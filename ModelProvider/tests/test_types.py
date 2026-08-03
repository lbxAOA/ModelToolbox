"""Test ModelProvider types and data structures."""

import pytest

from modeltoolbox_provider.types import (
    ChatMessage,
    ChatResult,
    ModelInfo,
    ProviderCapabilities,
    ToolCall,
    ToolDefinition,
)


def test_chat_message_creation():
    """Test ChatMessage creation."""
    msg = ChatMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.tool_calls is None


def test_chat_message_with_tool_calls():
    """Test ChatMessage with tool calls."""
    tool_call = ToolCall(id="call_1", name="search", arguments={"query": "test"})
    msg = ChatMessage(role="assistant", content="", tool_calls=[tool_call])
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0].name == "search"


def test_tool_definition():
    """Test ToolDefinition creation."""
    tool = ToolDefinition(
        name="search",
        description="Search the web",
        parameters={"type": "object", "properties": {"query": {"type": "string"}}},
    )
    assert tool.name == "search"
    assert "query" in tool.parameters["properties"]


def test_model_info():
    """Test ModelInfo creation."""
    model = ModelInfo(
        name="gpt-4",
        provider="openai",
        capabilities=("chat", "tools"),
        metadata={"context_length": 8192},
    )
    assert model.name == "gpt-4"
    assert "chat" in model.capabilities
    assert model.metadata["context_length"] == 8192


def test_chat_result():
    """Test ChatResult creation."""
    result = ChatResult(
        content="Hello!",
        model="gpt-4",
        provider="openai",
        usage={"prompt_tokens": 10, "completion_tokens": 5},
        finish_reason="stop",
    )
    assert result.content == "Hello!"
    assert result.usage["prompt_tokens"] == 10


def test_provider_capabilities():
    """Test ProviderCapabilities creation."""
    caps = ProviderCapabilities(
        name="test",
        chat=True,
        embed=False,
        models=True,
        stream=True,
        tools=True,
        local=False,
    )
    assert caps.chat is True
    assert caps.embed is False
    assert caps.stream is True


def test_immutable_types():
    """Test that types are immutable (frozen dataclasses)."""
    msg = ChatMessage(role="user", content="Hello")
    with pytest.raises(AttributeError):
        msg.content = "Goodbye"  # type: ignore
