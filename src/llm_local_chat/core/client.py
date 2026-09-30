"""Core LLM client and chat manager with agent routing and power levels."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Optional

import httpx

from llm_local_chat import AGENT_ROUTING, LOCAL_MODELS, POWER_LEVELS
from llm_local_chat.utils.logger import get_logger

logger = get_logger("client")


@dataclass
class ChatMessage:
    """A chat message."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ChatResponse:
    """A chat response with metadata."""

    content: str
    model: str
    agent: str = "athena"
    tokens_used: int = 0
    tokens_per_second: float = 0.0
    total_time_ms: float = 0.0
    done: bool = True


class OllamaClient:
    """Client for Ollama API — optimized for low-end PCs.

    Connects to locally running modified models (Athena, Mercatus, Cortex, LocalMind)
    that are quantized and optimized for CPU-only execution with minimal RAM.
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "athena",
        timeout: float = 300.0,
    ) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._http = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http.aclose()

    async def list_models(self) -> list[dict[str, Any]]:
        """List available local models."""
        try:
            resp = await self._http.get(f"{self.host}/api/tags")
            resp.raise_for_status()
            return resp.json().get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            resp = await self._http.get(f"{self.host}/api/tags")
            return resp.status_code == 200
        except Exception:
            return False

    async def chat(
        self,
        messages: list[ChatMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 4096,
        stream: bool = True,
    ) -> AsyncGenerator[ChatResponse, None]:
        """Send a chat request and stream the response."""

        # Build message list
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.model,
            "messages": api_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            },
        }

        start_time = time.time()
        total_content = ""
        tokens_used = 0

        try:
            if stream:
                async with self._http.stream(
                    "POST",
                    f"{self.host}/api/chat",
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            total_content += content
                            tokens_used += len(content.split())

                            yield ChatResponse(
                                content=content,
                                model=self.model,
                                tokens_used=tokens_used,
                                tokens_per_second=0.0,
                                total_time_ms=(time.time() - start_time) * 1000,
                                done=data.get("done", False),
                            )
                        except json.JSONDecodeError:
                            continue
            else:
                resp = await self._http.post(
                    f"{self.host}/api/chat",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                total_content = content
                tokens_used = len(content.split())

                yield ChatResponse(
                    content=content,
                    model=self.model,
                    tokens_used=tokens_used,
                    tokens_per_second=0.0,
                    total_time_ms=(time.time() - start_time) * 1000,
                    done=True,
                )

        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            yield ChatResponse(
                content=f"Error: {str(e)}",
                model=self.model,
                done=True,
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ChatResponse:
        """Generate a response (non-streaming)."""
        messages = [ChatMessage(role="user", content=prompt)]
        result = None
        async for resp in self.chat(
            messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        ):
            result = resp
        return result or ChatResponse(content="", model=self.model)


class AgentRouter:
    """Routes messages to the appropriate agent based on content."""

    def __init__(self) -> None:
        self._routing = AGENT_ROUTING

    def detect_agent(self, message: str) -> str:
        """Detect which agent should handle the message."""
        message_lower = message.lower()

        for agent, keywords in self._routing.items():
            if not keywords:
                continue
            for keyword in keywords:
                if keyword in message_lower:
                    return agent

        return "athena"  # Default agent


class ChatManager:
    """Manages chat sessions, agent routing, and power levels."""

    def __init__(self, client: OllamaClient) -> None:
        self.client = client
        self.router = AgentRouter()
        self._sessions: dict[str, list[ChatMessage]] = {}
        self._session_agents: dict[str, str] = {}  # session_id -> agent
        self._session_power: dict[str, str] = {}  # session_id -> power level
        self._auto_route: dict[str, bool] = {}  # session_id -> auto route

    def create_session(self, session_id: str, agent: str = "athena", power: str = "medium", auto_route: bool = True) -> None:
        """Create a new chat session."""
        self._sessions[session_id] = []
        self._session_agents[session_id] = agent
        self._session_power[session_id] = power
        self._auto_route[session_id] = auto_route

    def get_session(self, session_id: str) -> list[ChatMessage]:
        """Get messages for a session."""
        return self._sessions.get(session_id, [])

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to a session."""
        if session_id not in self._sessions:
            self.create_session(session_id)
        self._sessions[session_id].append(message)

    def clear_session(self, session_id: str) -> None:
        """Clear a session."""
        if session_id in self._sessions:
            self._sessions[session_id] = []

    def set_agent(self, session_id: str, agent: str) -> None:
        """Set the agent for a session."""
        self._session_agents[session_id] = agent

    def set_power(self, session_id: str, power: str) -> None:
        """Set the power level for a session."""
        self._session_power[session_id] = power

    def set_auto_route(self, session_id: str, auto_route: bool) -> None:
        """Enable/disable auto-routing for a session."""
        self._auto_route[session_id] = auto_route

    def get_agent(self, session_id: str) -> str:
        """Get the current agent for a session."""
        return self._session_agents.get(session_id, "athena")

    def get_power(self, session_id: str) -> str:
        """Get the current power level for a session."""
        return self._session_power.get(session_id, "medium")

    async def chat(
        self,
        session_id: str,
        message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[ChatResponse, None]:
        """Send a message and get streaming response with agent routing."""

        # Determine agent
        if self._auto_route.get(session_id, True):
            agent = self.router.detect_agent(message)
        else:
            agent = self.get_agent(session_id)

        # Get power level settings
        power = self.get_power(session_id)
        power_config = POWER_LEVELS.get(power, POWER_LEVELS["medium"])

        # Use power level settings if not overridden
        if temperature is None:
            temperature = power_config["temperature"]
        if max_tokens is None:
            max_tokens = power_config["max_tokens"]

        # Get system prompt for the agent
        system_prompt = LOCAL_MODELS.get(agent, LOCAL_MODELS["athena"])["system_prompt"]

        # Add user message
        self.add_message(session_id, ChatMessage(role="user", content=message))

        # Get response
        messages = self.get_session(session_id)
        async for resp in self.client.chat(
            messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            resp.agent = agent
            yield resp

        # Add assistant message
        if resp.content and not resp.content.startswith("Error:"):
            self.add_message(session_id, ChatMessage(role="assistant", content=resp.content))
