"""Tests for LLM Local Chat."""

import pytest
from llm_local_chat.core.client import ChatMessage, ChatManager, OllamaClient


class TestChatMessage:
    """Test ChatMessage model."""

    def test_create_message(self):
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_to_dict(self):
        msg = ChatMessage(role="assistant", content="Hi")
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "Hi"
        assert "timestamp" in d


class TestChatManager:
    """Test ChatManager."""

    def test_create_session(self):
        client = OllamaClient()
        manager = ChatManager(client)
        manager.create_session("test-session")
        assert "test-session" in manager._sessions

    def test_add_message(self):
        client = OllamaClient()
        manager = ChatManager(client)
        manager.create_session("test-session")
        manager.add_message("test-session", ChatMessage(role="user", content="Hello"))
        messages = manager.get_session("test-session")
        assert len(messages) == 1
        assert messages[0].content == "Hello"

    def test_clear_session(self):
        client = OllamaClient()
        manager = ChatManager(client)
        manager.create_session("test-session")
        manager.add_message("test-session", ChatMessage(role="user", content="Hello"))
        manager.clear_session("test-session")
        assert len(manager.get_session("test-session")) == 0


class TestOllamaClient:
    """Test OllamaClient."""

    def test_init(self):
        client = OllamaClient(host="http://localhost:11434", model="qwen2.5:12b")
        assert client.host == "http://localhost:11434"
        assert client.model == "qwen2.5:12b"

    def test_init_custom(self):
        client = OllamaClient(host="http://192.168.1.100:11434", model="llama3.1:8b")
        assert client.host == "http://192.168.1.100:11434"
        assert client.model == "llama3.1:8b"
