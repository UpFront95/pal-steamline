# pal-steamline

A stripped-down, opinionated fork of [PAL MCP Server](https://github.com/ppl-ai/pal-mcp-server), built specifically for use with Claude Code.

---

## Why this fork exists

The upstream PAL MCP server is powerful but ships with 15+ tools, a dynamic auto-mode engine, and a large configuration surface. When used inside Claude Code, a high tool count clutters the tool picker, inflates context overhead, and can lead to unpredictable tool selection.

**pal-steamline** cuts the noise. Nine tools and the auto-mode intelligence are removed, leaving a focused set of high-value developer workflows with deterministic model routing via a dual-provider (fast primary + expert validator) setup.

---

## What was removed

| Removed | Reason |
|---|---|
| `planner`, `analyze`, `secaudit`, `tracer`, `docgen`, `precommit`, `testgen` | Workflow tools rarely used; added friction to tool picker |
| `clink` | CLI-to-CLI bridge — not needed in Claude Code context |
| `challenge` | Adversarial debate tool — replaced by `consensus` for most use cases |
| `refactor` (standalone) | Merged into `codereview` as `mode="refactor"` — one tool, two modes |
| Auto-mode intelligence | Dynamic model selection removed; routing is now explicit and deterministic |
| HTTP cassette test suite | Was testing native OpenAI/Gemini paths this fork doesn't use |

---

## Tools

Eight tools remain. `version` and `listmodels` are always enabled; the rest can be individually disabled via `DISABLED_TOOLS`.

Multi-turn conversations persist within a server session using `continuation_id`. You can start a thread with `debug` and continue it with `codereview` — the full context carries over.

| Tool | What it does |
|---|---|
| `chat` | General Q&A, brainstorming, second opinions |
| `thinkdeep` | Extended step-by-step reasoning on hard problems |
| `debug` | Root-cause analysis workflow |
| `codereview` | Code quality, security, and perf audit — also handles `mode="refactor"` |
| `consensus` | Multi-model answer synthesis on a question |
| `apilookup` | Web/API reference lookup |
| `listmodels` | Lists available model aliases and their resolved names |
| `version` | Server version and build info |

---

## Model routing

Two providers, four aliases.

### Providers

| Provider | Role | Config |
|---|---|---|
| **Custom API** | Primary — fast and cheap for most tasks | `CUSTOM_API_URL` + `CUSTOM_API_KEY` |
| **OpenRouter** | Secondary — expert escalation and alternatives | `OPENROUTER_API_KEY` |

### Aliases

| Alias | Resolves to | Provider | Role |
|---|---|---|---|
| `mimo` | `xiaomi/mimo-v2-pro` | Custom API | **Default** |
| `gemini` | `google/gemini-3.1-pro-preview` | OpenRouter | **Expert escalation** |
| `gpt` | `openai/gpt-5.4` | OpenRouter | Alternative |
| `qwen` | `qwen/qwen3.6-plus` | OpenRouter | Alternative |

### Expert escalation

Workflow tools (`thinkdeep`, `debug`, `codereview`, `consensus`) run a two-pass analysis: the primary model (`mimo` by default) does the main work, then `EXPERT_MODEL` (`gemini`) runs the validation pass. Set `EXPERT_MODEL=""` to disable this and use a single model throughout.

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

# OpenRouter (secondary provider — gemini, gpt, qwen)
OPENROUTER_API_KEY=your-openrouter-key

# Optional: restrict which OpenRouter models are visible
# Leave unset to allow all models in conf/openrouter_models.json
OPENROUTER_ALLOWED_MODELS=google/gemini-3.1-pro-preview,openai/gpt-5.4,qwen/qwen3.6-plus

# Optional: disable individual tools (version and listmodels cannot be disabled)
DISABLED_TOOLS=apilookup,consensus

# Optional: language for AI responses (e.g. fr-FR, zh-CN)
LOCALE=
```

### Adding OpenRouter models

The full OpenRouter model catalogue is defined in `conf/openrouter_models.json`. Each entry can have `aliases` — adding a short alias there makes it available by that name in any tool call. The `OPENROUTER_ALLOWED_MODELS` env var then acts as a runtime allowlist on top of that catalogue.

### Using a different primary model

Set `DEFAULT_MODEL` to any alias or full model name visible in `listmodels`. To use a different Custom API endpoint (e.g. local Ollama), set `CUSTOM_API_URL=http://localhost:11434/v1` and leave `CUSTOM_API_KEY` empty.

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
