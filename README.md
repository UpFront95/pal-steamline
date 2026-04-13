# pal-STEAMline

A stripped-down, opinionated fork of [PAL MCP Server](https://github.com/ppl-ai/pal-mcp-server), built specifically for use with Claude Code.

---

## Why this fork exists

Claude Code is genuinely excellent at what it does. But even excellent tools have blind spots shaped by their training, architecture, and design goals — and a second opinion from a model with different training data, different construction, and a different focus is often worth having.

**pal-steamline** brings that into Claude Code. It gives you a set of purpose-built tools that reach out to other models mid-session: to review your code, debug a problem from a fresh angle, reason through something hard, or ask three models at once what they think. You stay in Claude Code. The conversation context carries over. You just get more perspectives.

The idea of this fork is legibility. The upstream PAL MCP server is powerful but ships with 15+ tools and a large configuration surface that creates noise in the tool picker and overhead in context. This fork strips it to tools with a clear, distinct purpose — each one does a specific thing you'd actually ask for. Some you'll use constantly. Some you'll reach for rarely. But when you need one, you'll know exactly which it is.

---

## Tools

Eight tools. `version` and `listmodels` are always on; the rest can be individually disabled via `DISABLED_TOOLS`.

Multi-turn conversations persist within a session using `continuation_id`. Start a thread with `debug` and continue it with `review` — full context carries over.

| Tool | What it does |
|---|---|
| `chat` | General Q&A, brainstorming, second opinions |
| `thinkdeep` | Extended step-by-step reasoning on hard problems |
| `debug` | Root-cause analysis workflow — for code that isn't working |
| `review` | Code quality, security, and performance audit — for code that works but needs checking |
| `cleanup` | Code smell detection, decomposition, and modernization (`mode="cleanup"` on the review tool) |
| `consensus` | Multi-model answer synthesis — asks 2–3 models and compares |
| `apilookup` | Web/API reference lookup |
| `listmodels` | Lists available model aliases and their resolved names |
| `version` | Server version and build info |

---

## Model routing

Five aliases across three providers.

### Providers

| Provider | Role | Config |
|---|---|---|
| **Custom API** | Primary — fast and cheap for most tasks | `CUSTOM_API_URL` + `CUSTOM_API_KEY` |
| **Mistral** | Native Mistral API | `MISTRAL_API_KEY` |
| **OpenRouter** | Secondary — expert escalation and alternatives | `OPENROUTER_API_KEY` |

### Aliases

| Alias | Resolves to | Provider | Role |
|---|---|---|---|
| `mimo` | `xiaomi/mimo-v2-pro` | Custom API | **Default** |
| `mistral` | `mistral-large-latest` | Mistral | Fast, strong reasoning |
| `gemini` | `google/gemini-3.1-pro-preview` | OpenRouter | **Expert escalation** |
| `gpt` | `openai/gpt-5.4` | OpenRouter | Alternative |
| `qwen` | `qwen/qwen3.6-plus` | OpenRouter | Alternative |

### Expert escalation

Workflow tools (`thinkdeep`, `debug`, `review`, `consensus`) run a two-pass analysis: the primary model does the main work, then `EXPERT_MODEL` (`gemini` by default) runs the validation pass. Set `EXPERT_MODEL=""` to disable and use a single model throughout.

---

## Installation

Requires Python 3.9+.

```bash
git clone <repo-url> pal-steamline
cd pal-steamline
python -m venv .pal_venv
source .pal_venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your keys
```

### Claude Code configuration

Add to your Claude Code MCP config (usually `~/.claude.json` or project-level `.mcp.json`):

```json
{
  "mcpServers": {
    "pal": {
      "command": "/absolute/path/to/pal-steamline/.pal_venv/bin/python",
      "args": ["/absolute/path/to/pal-steamline/server.py"]
    }
  }
}
```

Run `./run-server.sh -c` to generate the exact paths for your system.

---

## Configuration

All configuration is via `.env`. Copy `.env.example` for the full reference. The key variables:

```env
# Model routing
DEFAULT_MODEL=mimo
EXPERT_MODEL=gemini

# Custom API (primary provider — mimo)
CUSTOM_API_URL=https://your-custom-endpoint.com/v1
CUSTOM_API_KEY=your-key

# Mistral
MISTRAL_API_KEY=your-mistral-key

# OpenRouter (gemini, gpt, qwen)
OPENROUTER_API_KEY=your-openrouter-key

# Optional: restrict which OpenRouter models are visible
OPENROUTER_ALLOWED_MODELS=google/gemini-3.1-pro-preview,openai/gpt-5.4,qwen/qwen3.6-plus

# Optional: disable individual tools (version and listmodels cannot be disabled)
DISABLED_TOOLS=apilookup,consensus

# Optional: language for AI responses (e.g. fr-FR, zh-CN)
LOCALE=
```

### Adding OpenRouter models

The full OpenRouter model catalogue is defined in `conf/openrouter_models.json`. Each entry can have `aliases` — adding a short alias there makes it available by that name in any tool call. The `OPENROUTER_ALLOWED_MODELS` env var acts as a runtime allowlist on top of that catalogue.

### Using a different primary model

Set `DEFAULT_MODEL` to any alias or full model name visible in `listmodels`. To use a local model (e.g. Ollama), set `CUSTOM_API_URL=http://localhost:11434/v1` and leave `CUSTOM_API_KEY` empty.

---

## Running quality checks

```bash
source .pal_venv/bin/activate
./code_quality_checks.sh        # lint + format + unit tests
python -m pytest tests/ -v -m "not integration"   # unit tests only
```

---

## Attribution

This project is an opinionated fork of [PAL MCP Server](https://github.com/ppl-ai/pal-mcp-server) by Fahad Gilani, which was itself derived from Zen MCP. The core tool engine, provider abstractions, conversation memory system, and MCP transport layer originate from that upstream work.
