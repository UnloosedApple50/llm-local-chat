"""Web server — FastAPI backend with ChatGPT-style interface."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from llm_local_chat import LOCAL_MODELS, POWER_LEVELS
from llm_local_chat.core.client import ChatManager, OllamaClient
from llm_local_chat.utils.logger import get_logger

logger = get_logger("web")

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "src" / "llm_local_chat" / "web" / "templates"
STATIC_DIR = BASE_DIR / "src" / "llm_local_chat" / "web" / "static"

# Initialize
app = FastAPI(title="LLM Local Chat", version="0.1.0")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Global state
client: Optional[OllamaClient] = None
chat_manager: Optional[ChatManager] = None


@app.on_event("startup")
async def startup():
    """Initialize client on startup."""
    global client, chat_manager
    client = OllamaClient()
    chat_manager = ChatManager(client)
    logger.info("LLM Local Chat started")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    if client:
        await client.close()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main chat interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": LOCAL_MODELS,
        "power_levels": POWER_LEVELS,
    })


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    available = await client.is_available() if client else False
    return {
        "status": "ok" if available else "error",
        "ollama_available": available,
        "model": client.model if client else None,
    }


@app.get("/api/models")
async def list_models():
    """List available models."""
    if not client:
        return {"models": []}
    models = await client.list_models()
    return {"models": models}


@app.get("/api/config")
async def get_config():
    """Get available agents and power levels."""
    return {
        "agents": {k: v for k, v in LOCAL_MODELS.items()},
        "power_levels": {k: v for k, v in POWER_LEVELS.items()},
    }


@app.post("/api/chat")
async def chat(request: Request):
    """Send a chat message and stream the response."""
    data = await request.json()
    message = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    agent = data.get("agent")  # None = auto-route
    power = data.get("power", "medium")
    auto_route = data.get("auto_route", True)
    temperature = data.get("temperature")
    max_tokens = data.get("max_tokens")

    if not message:
        return {"error": "Message is required"}

    # Update session settings
    if agent:
        chat_manager.set_agent(session_id, agent)
    if power:
        chat_manager.set_power(session_id, power)
    if auto_route is not None:
        chat_manager.set_auto_route(session_id, auto_route)

    async def generate():
        async for resp in chat_manager.chat(
            session_id=session_id,
            message=message,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield f"data: {json.dumps(resp.__dict__)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@app.post("/api/session/new")
async def new_session():
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    chat_manager.create_session(session_id)
    return {"session_id": session_id}


@app.post("/api/session/clear")
async def clear_session(request: Request):
    """Clear a chat session."""
    data = await request.json()
    session_id = data.get("session_id")
    if session_id:
        chat_manager.clear_session(session_id)
    return {"status": "ok"}


@app.post("/api/session/config")
async def config_session(request: Request):
    """Update session configuration."""
    data = await request.json()
    session_id = data.get("session_id")
    agent = data.get("agent")
    power = data.get("power")
    auto_route = data.get("auto_route")

    if not session_id:
        return {"error": "session_id is required"}

    if agent:
        chat_manager.set_agent(session_id, agent)
    if power:
        chat_manager.set_power(session_id, power)
    if auto_route is not None:
        chat_manager.set_auto_route(session_id, auto_route)

    return {
        "status": "ok",
        "agent": chat_manager.get_agent(session_id),
        "power": chat_manager.get_power(session_id),
    }


# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
