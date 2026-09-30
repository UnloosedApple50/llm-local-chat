# LLM Local Chat

> Interface de chat com IA local — otimizada para PCs fracos e antigos. Roda modelos 12B em CPU com apenas 2-4GB de RAM.

## 🤖 Nossas IAs Locais

| Nome | Base | Parâmetros | RAM mínima | Descrição |
|------|------|------------|------------|-----------|
| **Athena** | Qwen 2.5 12B | 12B | 4GB | Assistente geral — conversa, análise, código |
| **Mercatus** | Qwen 2.5 12B | 12B | 4GB | Especialista em vendas e trading |
| **Cortex** | Qwen 2.5 12B | 12B | 4GB | Orquestração multi-máquina |
| **LocalMind** | Qwen 2.5 4B | 4B | 2GB | Ultra leve — roda em qualquer PC |

## ⚡ Níveis de Potência

| Nível | Modelo | Max Tokens | Temperatura | Descrição |
|-------|--------|------------|-------------|-----------|
| **Minimal** | LocalMind 4B | 1024 | 0.5 | Mais rápido, menor qualidade |
| **Medium** | Athena 12B | 4096 | 0.7 | Equilíbrio (recomendado) |
| **Ultra** | Athena 12B | 8192 | 0.9 | Mais qualidade, mais lento |

## ✨ Características

- 🏠 **100% Local** — sem internet, sem API, sem custos
- 💻 **Otimizado para CPU** — não precisa de GPU
- 🧠 **Modelos 12B comprimidos** — quantização Q4_K_M/Q2_K
- 📦 **Baixo consumo de RAM** — 2-4GB suficiente
- 🌐 **Interface web estilo ChatGPT** — familiar e intuitiva
- 🔒 **Privacidade total** — dados nunca saem do seu PC
- ⚡ **Streaming** — respostas em tempo real
- 🔄 **Roteamento automático** — detecta o agente ideal por mensagem
- 🎛️ **Níveis de potência** — ajuste velocidade vs qualidade

## 🚀 Instalação Rápida

### 1. Instalar Ollama

```bash
# macOS
curl -fsSL https://ollama.com/install.sh | sh

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: baixar de https://ollama.com/download
```

### 2. Baixar nossos modelos

```bash
# Athena 12B — uso geral (recomendado)
ollama pull qwen2.5:12b

# LocalMind 4B — PCs com 2GB RAM
ollama pull qwen2.5:4b
```

### 3. Instalar LLM Local Chat

```bash
git clone https://github.com/UnloosedApple50/llm-local-chat.git
cd llm-local-chat
pip install -e ".[dev]"
```

### 4. Iniciar

```bash
llm-chat start
```

Abra **http://localhost:8080** no navegador.

## 📋 Comandos CLI

| Comando | Descrição |
|---------|-----------|
| `llm-chat start` | Inicia o servidor web |
| `llm-chat list-models` | Lista modelos disponíveis |
| `llm-chat pull <model>` | Baixa um modelo |
| `llm-chat chat <msg>` | Envia uma mensagem (modo CLI) |

## 🎯 Modelos Suportados

### Nossas IAs (modificadas para uso local)

```bash
# Athena 12B — uso geral (recomendado)
ollama pull qwen2.5:12b

# LocalMind 4B — PCs com 2GB RAM
ollama pull qwen2.5:4b
```

### Modelos originais (também compatíveis)

```bash
ollama pull llama3.2:12b
ollama pull mistral:7b
ollama pull phi3:mini
```

## ⚙️ Configuração

Crie um arquivo `.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=athena
HOST=0.0.0.0
PORT=8080
MAX_TOKENS=4096
TEMPERATURE=0.7
```

## 📊 Performance Esperada

| PC | RAM | CPU | Tokens/seg |
|----|-----|-----|------------|
| Celeron + 4GB | 4GB | Celeron N4000 | ~2-5 t/s |
| i3 + 8GB | 8GB | i3-8100 | ~8-15 t/s |
| i5 + 8GB | 8GB | i5-7360U | ~10-20 t/s |
| i7 + 16GB | 16GB | i7-9700K | ~20-35 t/s |

## 🛠️ Desenvolvimento

```bash
# Rodar testes
pytest

# Rodar com coverage
pytest --cov=llm_local_chat --cov-report=html

# Lint
ruff check src tests

# Type check
mypy src
```

## 📁 Estrutura do Projeto

```
src/llm_local_chat/
├── core/
│   └── client.py          # Cliente Ollama + gerenciador de chat + roteamento
├── web/
│   ├── server.py        # Servidor FastAPI
│   ├── templates/
│   │   └── index.html   # Interface web
│   └── static/
│       └── style.css    # Estilos CSS
├── utils/
│   └── logger.py        # Logging
└── cli.py               # Interface CLI
tests/
└── test_client.py       # Testes
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

---

**Feito com 💙 para quem tem PCs fracos mas quer IA de qualidade!**
