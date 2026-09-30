"""LLM Local Chat — Local LLM chat interface optimized for low-end PCs.

Branded local AI models (modified for local execution):
- Athena: General assistant (code, analysis, chat) — 12B
- Mercatus: Sales & trading specialist — 12B
- Cortex: Multi-machine orchestration — 12B
- LocalMind: Ultra-lightweight for very weak PCs — 4B

All models are modified versions of open-source LLMs (Qwen 2.5, Llama 3.1, DeepSeek)
optimized to run locally with 2-4GB RAM using quantization and CPU offloading.

Power levels (like Hermes):
- minimal: Fastest, lowest quality (4B model, low tokens)
- medium: Balanced (12B model, medium tokens)
- ultra: Highest quality (12B model, high tokens, more context)
"""

__version__ = "0.1.0"

# Branded model names (modified for local execution)
LOCAL_MODELS = {
    "athena": {
        "base": "Qwen 2.5 12B",
        "description": "General assistant — code, analysis, chat",
        "ram_gb": 4,
        "disk_gb": 7,
        "quantization": "Q4_K_M",
        "system_prompt": "You are Athena, a helpful general assistant. You can help with coding, analysis, writing, and general questions. Be concise and clear.",
    },
    "mercatus": {
        "base": "Qwen 2.5 12B",
        "description": "Sales & trading specialist",
        "ram_gb": 4,
        "disk_gb": 7,
        "quantization": "Q4_K_M",
        "system_prompt": "You are Mercatus, a sales and trading expert. You provide actionable advice on sales strategies, trading analysis, risk management, and financial decisions.",
    },
    "cortex": {
        "base": "Qwen 2.5 12B",
        "description": "Multi-machine orchestration assistant",
        "ram_gb": 4,
        "disk_gb": 7,
        "quantization": "Q4_K_M",
        "system_prompt": "You are Cortex, a multi-machine orchestration expert. You help manage distributed computing, task scheduling, and cluster management.",
    },
    "localmind": {
        "base": "Qwen 2.5 4B",
        "description": "Ultra-lightweight for very weak PCs",
        "ram_gb": 2,
        "disk_gb": 3,
        "quantization": "Q4_K_M",
        "system_prompt": "You are LocalMind, a lightweight assistant for low-end PCs. You provide quick, concise answers while using minimal resources.",
    },
}

# Power levels (like Hermes)
POWER_LEVELS = {
    "minimal": {
        "model": "localmind",
        "max_tokens": 1024,
        "temperature": 0.5,
        "description": "Fastest, lowest quality — for very weak PCs",
    },
    "medium": {
        "model": "athena",
        "max_tokens": 4096,
        "temperature": 0.7,
        "description": "Balanced speed and quality — recommended",
    },
    "ultra": {
        "model": "athena",
        "max_tokens": 8192,
        "temperature": 0.9,
        "description": "Highest quality, slower — for complex tasks",
    },
}

# Agent routing rules (keyword-based)
AGENT_ROUTING = {
    "mercatus": [
        "sales", "trading", "revenue", "profit", "market", "investment",
        "stock", "trade", "deal", "customer", "pricing", "negotiation",
        "vendas", "trading", "receita", "lucro", "mercado", "investimento",
        "ação", "negócio", "cliente", "preço", "negociação",
    ],
    "cortex": [
        "cluster", "orchestration", "distributed", "server", "node", "task",
        "schedule", "deploy", "docker", "kubernetes", "load balance",
        "cluster", "orquestração", "distribuído", "servidor", "nó", "tarefa",
        "agendar", "deploy", "docker", "kubernetes", "balanceamento",
    ],
    "athena": [],  # Default agent
}
