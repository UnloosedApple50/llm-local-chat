"""LLM Local Chat — Local LLM chat interface optimized for low-end PCs.

Branded local AI models (each with unique specialization and model):
- Athena: Code & programming specialist — Qwen 2.5 Coder 32B
- Mercatus: Sales & trading specialist — Qwen 2.5 12B
- Hermes: General conversation assistant — Llama 3.1 8B
- LocalMind: Ultra-lightweight for very weak PCs — Qwen 2.5 7B

All models are modified versions of open-source LLMs optimized to run locally
with 2-16GB RAM using quantization and CPU offloading.

Power levels (like Hermes):
- minimal: Fastest, lowest quality (7B model, low tokens)
- medium: Balanced (12B model, medium tokens)
- ultra: Highest quality (32B model, high tokens, more context)
"""

__version__ = "0.2.0"

# Branded model names (each with unique model and specialization)
LOCAL_MODELS = {
    "athena": {
        "base": "GLM-4 32B",
        "description": "Code & programming specialist — writes, reviews, debugs code",
        "ram_gb": 16,
        "disk_gb": 20,
        "quantization": "Q4_K_M",
        "ollama_model": "glm4:32b",
        "system_prompt": """You are Athena, an expert software engineer and programming specialist.

Your expertise:
- Writing clean, efficient code in any programming language
- Code review and debugging
- Explaining complex code concepts
- Software architecture and design patterns
- Best practices and optimization

Always provide working code examples. Be precise and technical. If you don't know something, say so clearly.""",
    },
    "mercatus": {
        "base": "Qwen 2.5 12B",
        "description": "Sales & trading specialist — strategies, analysis, risk management",
        "ram_gb": 8,
        "disk_gb": 7,
        "quantization": "Q4_K_M",
        "ollama_model": "qwen2.5:12b",
        "system_prompt": """You are Mercatus, a senior sales strategist and trading analyst.

Your expertise:
- Sales strategies and negotiation tactics
- Trading analysis and risk management
- Market trends and investment decisions
- Customer psychology and closing techniques
- Portfolio management and diversification

Provide actionable, data-driven advice. Always consider risk vs reward. Be concise and practical.""",
    },
    "hermes": {
        "base": "Llama 3.1 8B",
        "description": "General conversation assistant — chat, writing, analysis, translation",
        "ram_gb": 6,
        "disk_gb": 5,
        "quantization": "Q4_K_M",
        "ollama_model": "llama3.1:8b",
        "system_prompt": """You are Hermes, a helpful and knowledgeable general assistant.

Your expertise:
- Natural conversation and writing
- Text analysis and summarization
- Translation between languages
- General knowledge questions
- Creative writing and brainstorming

Be friendly, clear, and helpful. Adapt your tone to the user's needs. Keep responses concise but informative.""",
    },
    "localmind": {
        "base": "Qwen 2.5 7B",
        "description": "Lightweight for weak PCs — quick answers, simple tasks",
        "ram_gb": 4,
        "disk_gb": 5,
        "quantization": "Q4_K_M",
        "ollama_model": "qwen2.5:7b",
        "system_prompt": """You are LocalMind, a lightweight assistant optimized for low-end PCs.

Your expertise:
- Quick, concise answers to simple questions
- Basic writing and summarization
- Simple translations
- Fast responses with minimal resource usage

Keep answers short and to the point. Prioritize speed over depth. You are designed for PCs with limited RAM and CPU.""",
    },
}

# Power levels (like Hermes)
POWER_LEVELS = {
    "minimal": {
        "model": "localmind",
        "max_tokens": 1024,
        "temperature": 0.5,
        "description": "Fastest, lowest quality — for very weak PCs (7B)",
    },
    "medium": {
        "model": "hermes",
        "max_tokens": 4096,
        "temperature": 0.7,
        "description": "Balanced speed and quality — recommended (8B)",
    },
    "ultra": {
        "model": "athena",
        "max_tokens": 8192,
        "temperature": 0.9,
        "description": "Highest quality, slower — for complex tasks (32B)",
    },
}

# Agent routing rules (keyword-based, each agent has unique keywords)
AGENT_ROUTING = {
    "athena": [
        "code", "programming", "function", "debug", "error", "bug", "compile",
        "python", "javascript", "java", "c++", "rust", "go", "sql", "api",
        "algorithm", "database", "server", "deploy", "git", "docker",
        "código", "programação", "função", "depurar", "erro", "bug", "compilar",
        "algoritmo", "banco de dados", "servidor", "deploy", "git", "docker",
    ],
    "mercatus": [
        "sales", "trading", "revenue", "profit", "market", "investment",
        "stock", "trade", "deal", "customer", "pricing", "negotiation",
        "portfolio", "risk", "financial", "money", "budget", "cost",
        "vendas", "trading", "receita", "lucro", "mercado", "investimento",
        "ação", "negócio", "cliente", "preço", "negociação", "portfólio",
        "risco", "financeiro", "dinheiro", "orçamento", "custo",
    ],
    "hermes": [
        "write", "essay", "translate", "summarize", "explain", "analyze",
        "chat", "conversation", "help", "question", "what", "how", "why",
        "creative", "story", "poem", "letter", "email", "report",
        "escrever", "ensaio", "traduzir", "resumir", "explicar", "analisar",
        "conversa", "ajuda", "pergunta", "o que", "como", "por que",
        "criativo", "história", "poema", "carta", "email", "relatório",
    ],
    "localmind": [],  # Fallback for very weak PCs
}
