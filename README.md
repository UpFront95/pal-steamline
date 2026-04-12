# PAL MCP Server

A Model Context Protocol (MCP) server that connects AI CLI tools and IDE clients to multiple AI model providers within a single conversation thread.

**Supported CLIs:** Claude Code, Gemini CLI, Codex CLI, Qwen Code CLI, OpenCode CLI, Cursor IDE, VS Code  
**Supported providers:** Gemini, OpenAI, Azure OpenAI, X.AI, Ollama, OpenRouter, DIAL, Custom/local endpoints

## Requirements

- Python 3.9+
- Git
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- At least one API key from a supported provider

## Installation

**Option A: Clone and run**
```bash
git clone https://github.com/UpFront95/pal-steamline.git
cd pal-steamline
./run-server.sh        # macOS/Linux
./run-server.ps1       # Windows PowerShell
```

Auto-configures Claude Desktop, Claude Code, Gemini CLI, Codex CLI, Qwen CLI, and OpenCode CLI.

**Option B: uvx (no clone)**

Add to `~/.claude/settings.json` or `.mcp.json`:
```json
{
  "mcpServers": {
    "pal": {
      "command": "bash",
      "args": ["-c", "for p in $(which uvx 2>/dev/null) $HOME/.local/bin/uvx /opt/homebrew/bin/uvx /usr/local/bin/uvx uvx; do [ -x \"$p\" ] && exec \"$p\" --from git+https://github.com/UpFront95/pal-steamline.git pal-mcp-server; done"],
      "env": {
        "GEMINI_API_KEY": "your-key-here",
        "DEFAULT_MODEL": "auto"
      }
    }
  }
}
```

For other clients (Gemini CLI `~/.gemini/settings.json`, Codex CLI `~/.codex/config.toml`, Qwen Code CLI `~/.qwen/settings.json`, OpenCode CLI `~/.config/opencode/opencode.json`, Cursor IDE, VS Code), see [Getting Started](docs/getting-started.md) for per-client configuration snippets.

## Configuration

PAL activates any provider that has credentials set in your environment or `.env` file. See `.env.example` for all options.

Key environment variables:

| Variable | Description |
|----------|-------------|
| `DEFAULT_MODEL` | Model used when none is specified. Options: `auto`, `pro`, `flash`, `o3`, `o3-mini`, `o4-mini`, `o4-mini-high`, `gpt-5.2`, `gpt-5.2-pro`, `gpt-5.1-codex`, `gpt-5.1-codex-mini`, `gpt-5`, `gpt-5-mini`, `grok`, `opus-4.1`, `sonnet-4.1`, or any DIAL model. Defaults to `auto`. |
| `DEFAULT_THINKING_MODE_THINKDEEP` | Reasoning depth for `thinkdeep`: `minimal` (128 tokens), `low` (2K), `medium` (8K), `high` (16K, default), `max` (32K). |
| `DISABLED_TOOLS` | Comma-separated list of tools to disable. By default `analyze,refactor,testgen,secaudit,docgen,tracer` are disabled to save context window space. |
| `CONVERSATION_TIMEOUT_HOURS` / `MAX_CONVERSATION_TURNS` | Conversation thread limits. |
| `PAL_MCP_FORCE_ENV_OVERRIDE` | When `true`, `.env` values override system environment variables — useful when multiple AI tools conflict. Default: `false`. |
| `LOCALE` | Language for AI responses, e.g. `fr-FR`, `zh-CN`, `ja-JP`. Defaults to English. |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, or `ERROR`. |

**Model restrictions** (for cost control or compliance):
```env
OPENAI_ALLOWED_MODELS=o4-mini,gpt-5.1-codex-mini
GOOGLE_ALLOWED_MODELS=flash,pro
XAI_ALLOWED_MODELS=grok-3
DIAL_ALLOWED_MODELS=o3,gemini-2.5-pro
OPENROUTER_ALLOWED_MODELS=
```

**Azure OpenAI:**
```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# Optional: AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ALLOWED_MODELS, AZURE_MODELS_CONFIG_PATH
```

### Supported Models

| Provider | Models | Aliases |
|----------|--------|---------|
| OpenAI | `gpt-5.2`, `gpt-5.2-pro`, `gpt-5.1-codex`, `gpt-5.1-codex-mini`, `gpt-5`, `gpt-5-mini`, `o3`, `o3-mini`, `o4-mini`, `o4-mini-high` | `mini` → `o4-mini` |
| Gemini | `gemini-2.5-pro`, `gemini-2.5-flash` | `pro`, `flash` |
| X.AI | `grok-3`, `grok-3-fast` | `grok`, `grok3`, `grokfast` |
| DIAL | `o3`, `o4-mini`, Claude 4.1 Sonnet/Opus (with thinking), Gemini 2.5 models | `opus-4.1`, `sonnet-4.1`, `opus-4.1-thinking`, `sonnet-4.1-thinking` |
| OpenRouter | Many models via single API key | — |
| Custom | Ollama, vLLM, LM Studio, and any OpenAI-compatible endpoint | — |

Model capability data lives in per-provider JSON manifests under `conf/` and can be overridden with `*_MODELS_CONFIG_PATH` env vars.

## Tools

**Collaboration** *(enabled by default)*
- `chat` — Brainstorm, get second opinions, generate code
- `thinkdeep` — Extended reasoning and alternative perspectives
- `consensus` — Gather opinions from multiple models simultaneously
- `planner` — Interactive sequential planning

**Code Quality** *(enabled by default)*
- `codereview` — Multi-pass review with severity levels
- `debug` — Systematic root cause analysis
- `precommit` — Pre-commit validation

**Code Analysis** *(disabled by default — enable via `DISABLED_TOOLS`)*
- `refactor` — Refactoring analysis and suggestions
- `analyze` — Code assessment
- `secaudit` — Security audit
- `testgen` — Test generation
- `docgen` — Documentation generation
- `tracer` — Code tracing and dependency mapping

**Utilities**
- `apilookup` — Fetch current API/SDK documentation in a subprocess
- `challenge` — Critical analysis to counter reflexive agreement
- `listmodels` — Show configured providers and available models
- `version` — Display server version and configuration

## Features

- **Conversation continuity** — context is preserved across tools and models within a thread
- **Auto model selection** — the orchestrating CLI picks the appropriate model per subtask
- **Extended context** — delegate to models with larger context windows (e.g. Gemini 1M tokens)
- **Vision support** — analyze images with vision-enabled models
- **Local model support** — use Ollama or any OpenAI-compatible endpoint for offline/private inference
- **Large prompt support** — bypasses MCP's 25K token limit automatically
- **Selective tool loading** — disable unused tools with `DISABLED_TOOLS` to keep context windows lean
- **Locale support** — configure AI responses in your preferred language
- **Azure OpenAI support** — enterprise Azure-hosted model deployments
- **Code generation mode** — models with `allow_code_generation` enabled produce structured `<GENERATED-CODE>` blocks saved to `pal_generated.code` for your CLI to apply
- **Model manifest overrides** — customise model capabilities, aliases, and feature flags by editing or overriding the `conf/*.json` files

## Documentation

- [Getting Started](docs/getting-started.md)
- [Tools Reference](docs/tools/)
- [Configuration](docs/configuration.md)
- [Advanced Usage](docs/advanced-usage.md)
- [Custom Models](docs/custom_models.md)
- [Azure OpenAI](docs/azure_openai.md)
- [Locale Configuration](docs/locale-configuration.md)
- [Adding Providers](docs/adding_providers.md)
- [Adding Tools](docs/adding_tools.md)
- [Troubleshooting](docs/troubleshooting.md)
- [WSL Setup](docs/wsl-setup.md)
- [Testing](docs/testing.md)

## License

Apache 2.0 — see [LICENSE](LICENSE)