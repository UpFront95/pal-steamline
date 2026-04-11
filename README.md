# PAL MCP: Many Workflows. One Context.

<div align="center">

  <em>Your AI's PAL – a Provider Abstraction Layer</em><br />
  <sub><a href="docs/name-change.md">Formerly known as Zen MCP</a></sub>

  [PAL in action](https://github.com/user-attachments/assets/0d26061e-5f21-4ab1-b7d0-f883ddc2c3da)

👉 **[Watch more examples](#-watch-tools-in-action)**

### Your CLI + Multiple Models = Your AI Dev Team

**Use the 🤖 CLI you love:**  
[Claude Code](https://www.anthropic.com/claude-code) · [Gemini CLI](https://github.com/google-gemini/gemini-cli) · [Codex CLI](https://github.com/openai/codex) · [Qwen Code CLI](https://qwenlm.github.io/qwen-code-docs/) · [Cursor](https://cursor.com) · _and more_

**With multiple models within a single prompt:**  
Gemini · OpenAI · Azure OpenAI · X.AI/Grok · DIAL · OpenRouter · Ollama/local

</div>

---

## Why PAL MCP?

**Why rely on one AI model when you can orchestrate them all?**

A Model Context Protocol server that supercharges tools like [Claude Code](https://www.anthropic.com/claude-code), [Codex CLI](https://developers.openai.com/codex/cli), and IDE clients such as [Cursor](https://cursor.com). **PAL MCP connects your favorite AI tool to multiple AI models** for enhanced code analysis, problem-solving, and collaborative development.

### True AI Collaboration with Conversation Continuity

PAL supports **conversation threading** so your CLI can **discuss ideas with multiple AI models, exchange reasoning, get second opinions, and even run collaborative debates between models** to help you reach deeper insights and better solutions.

Your CLI always stays in control but gets perspectives from the best AI for each subtask. Context carries forward seamlessly across tools and models, enabling complex workflows like: code reviews with multiple models → automated planning → implementation → pre-commit validation.

> **You're in control.** Your CLI of choice orchestrates the AI team, but you decide the workflow. Craft powerful prompts that bring in Gemini Pro, GPT-5, Flash, or local offline models exactly when needed.

<details>
<summary><b>Reasons to Use PAL MCP</b></summary>

1. **Multi-Model Orchestration** - Coordinate Gemini Pro, O3, GPT-5, Grok, and local models to get the best analysis for each task
2. **Context Revival Magic** - Even after your CLI's context resets, continue conversations seamlessly
3. **Guided Workflows** - Systematic investigation phases prevent rushed analysis
4. **Extended Context Windows** - Delegate to Gemini (1M tokens) or O3 (200K tokens) for massive codebases
5. **True Conversation Continuity** - Full context flows across tools and models
6. **Professional Code Reviews** - Multi-pass analysis with severity levels and consensus from multiple AI experts
7. **Automatic Model Selection** - `auto` mode picks the right model for each subtask
8. **Local Model Support** - Run Llama or other models locally for complete privacy and zero API costs
9. **Bypass MCP Token Limits** - Automatically works around MCP's output limits for large prompts

**Think of it as Claude Code _for_ Claude Code.** This MCP isn't magic. It's just **super-glue**.

> **You are the AI — Actually Intelligent.**
</details>

## Quick Start (5 minutes)

**Prerequisites:** Python 3.10+, Git

**1. Get API Keys** (choose one or more):
- **[OpenRouter](https://openrouter.ai/)** - Access multiple models with one API
- **[Gemini](https://makersuite.google.com/app/apikey)** - Google's latest models (flash, pro)
- **[OpenAI](https://platform.openai.com/api-keys)** - O3, GPT-5 series, Codex
- **[Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)** - Enterprise Azure-hosted deployments
- **[X.AI](https://console.x.ai/)** - Grok models
- **[DIAL](https://dialx.ai/)** - Unified enterprise model access
- **[Ollama](https://ollama.ai/)** - Local models (free, no API key needed)

**2. Install:**

**Option A: Clone and Automatic Setup** (recommended)
```bash
git clone https://github.com/UpFront95/pal-steamline.git
cd pal-steamline

# Handles everything: venv setup, dependencies, .env config, MCP auto-configuration
# Auto-configures Claude Desktop, Claude Code, Gemini CLI, Codex CLI
./run-server.sh        # Linux/macOS
# .\run-server.ps1     # Windows (PowerShell)
```

**Option B: Instant Setup with [uvx](https://docs.astral.sh/uv/getting-started/installation/)**
```json
// Add to ~/.claude/settings.json or .mcp.json
// Don't forget to add your API keys under env
{
  "mcpServers": {
    "pal": {
      "command": "bash",
      "args": ["-c", "for p in $(which uvx 2>/dev/null) $HOME/.local/bin/uvx /opt/homebrew/bin/uvx /usr/local/bin/uvx uvx; do [ -x \"$p\" ] && exec \"$p\" --from git+https://github.com/UpFront95/pal-steamline.git pal-mcp-server; done; echo 'uvx not found' >&2; exit 1"],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:~/.local/bin",
        "GEMINI_API_KEY": "your-key-here",
        "DISABLED_TOOLS": "analyze,refactor,testgen,secaudit,docgen,tracer",
        "DEFAULT_MODEL": "auto"
      }
    }
  }
}
```

**Option C: Manual MCP Config** (after running `./run-server.sh` once to create the venv)
```json
// ~/.claude/settings.json or .mcp.json
{
  "mcpServers": {
    "pal": {
      "command": "/path/to/pal-steamline/.pal_venv/bin/python",
      "args": ["/path/to/pal-steamline/server.py"]
    }
  }
}
```

**3. Start Using!**
```
"Use pal to analyze this code for security issues with gemini pro"
"Debug this error with o3 and then get flash to suggest optimizations"
"Plan the migration strategy with pal, get consensus from multiple models"
"Do a codereview using pro and o3, then use planner to create a fix strategy"
```

👉 **[Complete Setup Guide](docs/getting-started.md)** with detailed installation, configuration for Gemini / Codex / Qwen, and troubleshooting
👉 **[Cursor & VS Code Setup](docs/getting-started.md#ide-clients)** for IDE integration instructions
📺 **[Watch tools in action](#-watch-tools-in-action)** to see real-world examples

## Providers

PAL activates any provider that has credentials in your `.env`. See `.env.example` for full configuration details.

| Provider | Env Variable(s) | Notes |
|---|---|---|
| **Google Gemini** | `GEMINI_API_KEY` | `flash`, `pro` (gemini-2.5-flash/pro) |
| **OpenAI** | `OPENAI_API_KEY` | GPT-5 series, O3, O4-mini, Codex |
| **Azure OpenAI** | `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` | Azure-hosted GPT deployments |
| **X.AI / Grok** | `XAI_API_KEY` | `grok`, `grokfast` (grok-3/grok-3-fast) |
| **DIAL** | `DIAL_API_KEY` | O3, O4-mini, Claude 4.1, Gemini 2.5 via DIAL |
| **OpenRouter** | `OPENROUTER_API_KEY` | Multi-model unified access |
| **Custom / Ollama** | `CUSTOM_API_URL` | Any local OpenAI-compatible endpoint |

## Models

Key model shorthands (see `.env.example` for the full list):

| Shorthand | Full Model | Provider |
|---|---|---|
| `flash` | gemini-2.5-flash | Google Gemini |
| `pro` | gemini-2.5-pro | Google Gemini |
| `gpt-5.2` | gpt-5.2 | OpenAI |
| `gpt-5.2-pro` | gpt-5.2-pro | OpenAI |
| `gpt-5.1-codex` | gpt-5.1-codex | OpenAI |
| `gpt-5.1-codex-mini` | gpt-5.1-codex-mini | OpenAI |
| `gpt-5` | gpt-5 | OpenAI |
| `gpt-5-mini` | gpt-5-mini | OpenAI |
| `o3` | o3 | OpenAI / DIAL |
| `o4-mini` | o4-mini | OpenAI / DIAL |
| `grok` | grok-3 | X.AI |
| `grokfast` | grok-3-fast | X.AI |
| `sonnet-4.1` | claude-sonnet-4.1 | DIAL |
| `opus-4.1` | claude-opus-4.1 | DIAL |

Set `DEFAULT_MODEL=auto` (the default) to let your CLI automatically pick the best model for each task.

## Core Tools

> **Note:** Each tool's workflow description consumes context window space even when not in use. To optimize performance, some tools are disabled by default. See [Tool Configuration](#tool-configuration) below to enable them.

**Collaboration & Planning** *(Enabled by default)*
- **[`chat`](docs/tools/chat.md)** - General AI conversation, brainstorming, second opinions, and collaborative problem-solving
- **[`thinkdeep`](docs/tools/thinkdeep.md)** - Extended reasoning with configurable thinking modes (minimal/low/medium/high/max)
- **[`planner`](docs/tools/planner.md)** - Break down complex projects into structured, actionable plans
- **[`consensus`](docs/tools/consensus.md)** - Get expert opinions from multiple AI models with stance steering
- **[`clink`](docs/tools/clink.md)** - CLI-to-CLI bridge: connect external AI CLIs (Gemini CLI, Codex, Claude Code) into your workflow

**Code Analysis & Quality** *(Enabled by default)*
- **[`codereview`](docs/tools/codereview.md)** - Professional reviews with severity levels and actionable feedback
- **[`precommit`](docs/tools/precommit.md)** - Validate changes before committing, prevent regressions
- **[`debug`](docs/tools/debug.md)** - Systematic root cause analysis with hypothesis tracking

**Utilities** *(Enabled by default)*
- **[`apilookup`](docs/tools/apilookup.md)** - Current-year API/SDK documentation lookups; prevents outdated training-data responses
- **[`challenge`](docs/tools/challenge.md)** - Prevent reflexive agreement with critical analysis
- **[`listmodels`](docs/tools/listmodels.md)** - List available AI models across all configured providers
- **[`version`](docs/tools/version.md)** - Server version and configuration info

**Advanced Tools** *(Disabled by default — [enable below](#tool-configuration))*
- **[`analyze`](docs/tools/analyze.md)** - Architecture, patterns, and dependency analysis across entire codebases
- **[`refactor`](docs/tools/refactor.md)** - Intelligent code refactoring with decomposition focus
- **[`testgen`](docs/tools/testgen.md)** - Comprehensive test generation with edge cases
- **[`secaudit`](docs/tools/secaudit.md)** - Security audits with OWASP Top 10 analysis
- **[`docgen`](docs/tools/docgen.md)** - Generate documentation with complexity analysis
- **[`tracer`](docs/tools/tracer.md)** - Static analysis for call-flow mapping

<details>
<summary><b id="tool-configuration">👉 Tool Configuration</b></summary>

### Default Configuration

To optimize context window usage, only essential tools are enabled by default:

**Enabled by default:**
- `chat`, `thinkdeep`, `planner`, `consensus`, `clink` — Collaboration tools
- `codereview`, `precommit`, `debug` — Code quality tools
- `apilookup`, `challenge`, `listmodels`, `version` — Utilities

**Disabled by default** (`DISABLED_TOOLS=analyze,refactor,testgen,secaudit,docgen,tracer`):
- `analyze`, `refactor`, `testgen`, `secaudit`, `docgen`, `tracer`

### Enabling Additional Tools

**Option 1: Edit your .env file**
```bash
# Default (from .env.example)
DISABLED_TOOLS=analyze,refactor,testgen,secaudit,docgen,tracer

# Enable analyze tool by removing it from the list
DISABLED_TOOLS=refactor,testgen,secaudit,docgen,tracer

# Enable all tools
DISABLED_TOOLS=
```

**Option 2: Configure in MCP settings**
```json
{
  "mcpServers": {
    "pal": {
      "env": {
        "DISABLED_TOOLS": "refactor,testgen,secaudit,docgen,tracer",
        "DEFAULT_MODEL": "auto",
        "DEFAULT_THINKING_MODE_THINKDEEP": "high",
        "GEMINI_API_KEY": "your-gemini-key",
        "OPENAI_API_KEY": "your-openai-key",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note:**
- `version` and `listmodels` cannot be disabled
- After changing tool configuration, restart your Claude session for changes to take effect

</details>

## Configuration

Key environment variables (see `.env.example` for the full reference):

| Variable | Default | Description |
|---|---|---|
| `DEFAULT_MODEL` | `auto` | Model to use; `auto` lets the CLI pick the best model per task |
| `DEFAULT_THINKING_MODE_THINKDEEP` | `high` | Thinking depth for ThinkDeep: `minimal` / `low` / `medium` / `high` / `max` |
| `DISABLED_TOOLS` | `analyze,refactor,testgen,secaudit,docgen,tracer` | Comma-separated tools to disable |
| `LOCALE` | _(English)_ | Language for AI responses, e.g. `fr-FR`, `zh-CN`, `ja-JP` |
| `PAL_MCP_FORCE_ENV_OVERRIDE` | `false` | When `true`, `.env` values override system environment variables |
| `CONVERSATION_TIMEOUT_HOURS` | `24` | How long conversation threads persist in memory |
| `MAX_CONVERSATION_TURNS` | `40` | Maximum turns per AI-to-AI conversation thread |

## 📺 Watch Tools In Action

<details>
<summary><b>Chat Tool</b> - Collaborative decision making and multi-turn conversations</summary>

**Picking Redis vs Memcached:**

[Chat Redis or Memcached_web.webm](https://github.com/user-attachments/assets/41076cfe-dd49-4dfc-82f5-d7461b34705d)

**Multi-turn conversation with continuation:**

[Chat With Gemini_web.webm](https://github.com/user-attachments/assets/37bd57ca-e8a6-42f7-b5fb-11de271e95db)

</details>

<details>
<summary><b>Consensus Tool</b> - Multi-model debate and decision making</summary>

**Multi-model consensus debate:**

[PAL Consensus Debate](https://github.com/user-attachments/assets/76a23dd5-887a-4382-9cf0-642f5cf6219e)

</details>

<details>
<summary><b>PreCommit Tool</b> - Comprehensive change validation</summary>

**Pre-commit validation workflow:**

<div align="center">
  <img src="https://github.com/user-attachments/assets/584adfa6-d252-49b4-b5b0-0cd6e97fb2c6" width="950">
</div>

</details>

<details>
<summary><b>API Lookup Tool</b> - Current vs outdated API documentation</summary>

**Without PAL - outdated APIs:**

[API without PAL](https://github.com/user-attachments/assets/01a79dc9-ad16-4264-9ce1-76a56c3580ee)

**With PAL - current APIs:**

[API with PAL](https://github.com/user-attachments/assets/5c847326-4b66-41f7-8f30-f380453dce22)

</details>

<details>
<summary><b>Challenge Tool</b> - Critical thinking vs reflexive agreement</summary>

**Without PAL:**

![without_pal@2x](https://github.com/user-attachments/assets/64f3c9fb-7ca9-4876-b687-25e847edfd87)

**With PAL:**

![with_pal@2x](https://github.com/user-attachments/assets/9d72f444-ba53-4ab1-83e5-250062c6ee70)

</details>

## Key Features

**AI Orchestration**
- **Auto model selection** - `auto` mode picks the right AI for each task
- **Multi-model workflows** - Chain different models in single conversations
- **Conversation continuity** - Context preserved across tools and models
- **[Context revival](docs/context-revival.md)** - Continue conversations even after context resets

**Model Support**
- **7 providers** - Gemini, OpenAI, Azure OpenAI, X.AI/Grok, DIAL, OpenRouter, Custom/Ollama
- **Latest models** - GPT-5.2, Gemini 2.5 Pro/Flash, O3, Grok-3, Claude 4.1, and local Llama
- **[Thinking modes](docs/advanced-usage.md#thinking-modes)** - Control reasoning depth vs cost
- **Vision support** - Analyze images, diagrams, screenshots

**Developer Experience**
- **Guided workflows** - Systematic investigation prevents rushed analysis
- **Smart file handling** - Auto-expand directories, manage token limits
- **[Large prompt support](docs/advanced-usage.md#working-with-large-prompts)** - Bypass MCP's token limits

## Example Workflows

**Multi-model Code Review:**
```
"Perform a codereview using pro and o3, then use planner to create a fix strategy"
```
→ Claude reviews code systematically → Consults Gemini Pro → Gets O3's perspective → Creates unified action plan

**Collaborative Debugging:**
```
"Debug this race condition with max thinking mode, then validate the fix with precommit"
```
→ Deep investigation → Expert analysis → Solution implementation → Pre-commit validation

**Architecture Planning:**
```
"Plan our microservices migration, get consensus from pro and o3 on the approach"
```
→ Structured planning → Multiple expert opinions → Consensus building → Implementation roadmap

👉 **[Advanced Usage Guide](docs/advanced-usage.md)** for complex workflows, model configuration, and power-user features

## Testing

```bash
# Activate virtual environment
source .pal_venv/bin/activate

# Run linting, formatting, and unit tests
./code_quality_checks.sh       # Linux/macOS
# .\code_quality_checks.ps1    # Windows

# Run unit tests directly
python -m pytest tests/ -v -m "not integration"

# Run simulator tests (requires configured API keys)
python communication_simulator_test.py --quick          # 6 essential tests
python communication_simulator_test.py --individual chat  # single test

# Run integration tests
./run_integration_tests.sh
```

## Quick Links

**📖 Documentation**
- [Docs Overview](docs/index.md) - High-level map of major guides
- [Getting Started](docs/getting-started.md) - Complete setup guide
- [Tools Reference](docs/tools/) - All tools with examples
- [Advanced Usage](docs/advanced-usage.md) - Power user features
- [Configuration](docs/configuration.md) - Environment variables, restrictions
- [Adding Providers](docs/adding_providers.md) - Provider-specific setup
- [Model Ranking Guide](docs/model_ranking.md) - How auto-mode selects models

**🔧 Setup & Support**
- [WSL Setup](docs/wsl-setup.md) - Windows users
- [Troubleshooting](docs/troubleshooting.md) - Common issues
- [Contributing](docs/contributions.md) - Code standards, PR process

## License

Apache 2.0 License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with the power of **Multi-Model AI** collaboration 🤝
- **A**ctual **I**ntelligence by real Humans
- [MCP (Model Context Protocol)](https://modelcontextprotocol.com)
- [Codex CLI](https://developers.openai.com/codex/cli)
- [Claude Code](https://claude.ai/code)
- [Gemini](https://ai.google.dev/)
- [OpenAI](https://openai.com/)
- [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=BeehiveInnovations/pal-mcp-server&type=Date)](https://www.star-history.com/#BeehiveInnovations/pal-mcp-server&Date)
