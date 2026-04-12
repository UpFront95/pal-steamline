# PAL MCP Server

A Model Context Protocol (MCP) server that connects AI CLI tools and IDE clients to multiple AI model providers within a single conversation thread.

**Supported CLIs:** Claude Code, Gemini CLI, Codex CLI, Qwen Code CLI  
**Supported providers:** Gemini, OpenAI, Anthropic, Azure, X.AI, Ollama, OpenRouter, DIAL

## Requirements

- Python 3.10+
- Git
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- At least one API key from a supported provider

## Installation

**Option A: Clone and run**  
```bash
git clone https://github.com/BeehiveInnovations/pal-mcp-server.git
cd pal-mcp-server
./run-server.sh
```

Auto-configures Claude Desktop, Claude Code, Gemini CLI, Codex CLI, and Qwen CLI.

**Option B: uvx (no clone)**

Add to `~/.claude/settings.json` or `.mcp.json`:
```json
{
  "mcpServers": {
    "pal": {
      "command": "bash",
      "args": ["-c", "for p in $(which uvx 2>/dev/null) $HOME/.local/bin/uvx /opt/homebrew/bin/uvx /usr/local/bin/uvx uvx; do [ -x \"$p\" ] && exec \"$p\" --from git+https://github.com/BeehiveInnovations/pal-mcp-server pal-mcp-server; done"],
      "env": {
        "GEMINI_API_KEY": "your-key-here",
        "DEFAULT_MODEL": "gemini-2.5-flash"
      }
    }
  }
}
```

## Configuration

PAL activates any provider that has credentials set in your environment or `.env` file. See `.env.example` for all options.

Key environment variables:
- `DEFAULT_MODEL` — model used when none is specified
- `DEFAULT_THINKING_MODE_THINKDEEP` — reasoning depth for `thinkdeep` tool
- `CONVERSATION_TIMEOUT_HOURS` / `MAX_CONVERSATION_TURNS` — conversation limits
- `LOG_LEVEL`

## Tools

**Collaboration**
- `chat` — Brainstorm, get second opinions, generate code
- `thinkdeep` — Extended reasoning and alternative perspectives
- `consensus` — Gather opinions from multiple models simultaneously

**Code Analysis**
- `codereview` — Multi-pass review with severity levels
- `debug` — Systematic root cause analysis
- `refactor` — Refactoring analysis and suggestions
- `analyze` — Code assessment
- `secaudit` — Security audit
- `testgen` — Test generation
- `docgen` — Documentation generation
- `tracer` — Code tracing and dependency mapping
- `precommit` — Pre-commit validation

**Utilities**
- `apilookup` — Fetch current API/SDK documentation in a subprocess
- `challenge` — Critical analysis to counter reflexive agreement
- `planner` — Interactive sequential planning
- `listmodels` — Show configured providers and available models
- `version` — Display server version and configuration

## Features

- **Conversation continuity** — context is preserved across tools and models within a thread
- **Auto model selection** — the orchestrating CLI picks the appropriate model per subtask
- **Extended context** — delegate to models with larger context windows (e.g. Gemini 1M tokens)
- **Vision support** — analyze images with vision-enabled models
- **Local model support** — use Ollama for offline/private inference
- **Large prompt support** — bypasses MCP's 25K token limit automatically

## Documentation

- [Getting Started](docs/getting-started.md)
- [Tools Reference](docs/tools/)
- [Advanced Usage](docs/advanced-usage.md)
- [Configuration](docs/configuration.md)
- [Adding Providers](docs/adding_providers.md)
- [Troubleshooting](docs/troubleshooting.md)
- [WSL Setup](docs/wsl-setup.md)

## License

Apache 2.0 — see [LICENSE](LICENSE)