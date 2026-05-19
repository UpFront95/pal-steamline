# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

**pal-steamline** is a stripped-down, opinionated fork of PAL MCP Server, built specifically for use with Claude Code. It's an MCP (Model Context Protocol) server that exposes AI-powered tools for code analysis, review, and collaborative thinking.

### Fork Philosophy

The upstream PAL MCP server is powerful but ships with 15+ tools and a large configuration surface. This fork prioritizes **legibility** — each tool has a clear, distinct purpose. The result is 4 core tools (plus 3 utility tools) that you'll actually use:

- **chat** — General Q&A, brainstorming, second opinions
- **thinkdeep** — Extended step-by-step reasoning on hard problems
- **consensus** — Multi-model answer synthesis (asks 2-3 models and compares)
- **review** — Code quality, security, and performance audit for working code

Plus utility tools: **apilookup**, **listmodels**, **version**

### Architecture

The server is built on the MCP protocol and runs as a stdio subprocess. Key components:

- **server.py** — MCP entrypoint, tool routing, conversation lifecycle management
- **tools/** — Tool implementations (SimpleTool base class for consistency)
- **providers/** — AI provider integrations (Custom API, Mistral, OpenRouter)
- **systemprompts/** — System prompts for each tool
- **utils/** — Shared utilities (conversation memory, token management, file handling)
- **tests/** — Unit tests (pytest)
- **simulator_tests/** — Integration tests for multi-turn conversations

### Model Routing

Five aliases across three providers:

| Alias | Resolves to | Provider | Role |
|---|---|---|---|
| `mimo` | `xiaomi/mimo-v2.5-pro` | Custom API | **Default** — fast and cheap |
| `mistral` | `mistral-large-latest` | Mistral | Fast, strong reasoning |
| `gemini` | `google/gemini-3.1-pro-preview` | OpenRouter | **Expert escalation** |
| `gpt` | `openai/gpt-5.4` | OpenRouter | Alternative expert model |

**Expert escalation**: Workflow tools (thinkdeep, review, consensus) run a two-pass analysis — primary model does main work, then `EXPERT_MODEL` (gemini by default) validates. Set `EXPERT_MODEL=""` to disable.

### Conversation Continuity

Multi-turn conversations are supported via `continuation_id`. Start a thread with any tool, then continue with the same or different tool — full context carries over. The server manages conversation state in-memory with intelligent token budgeting.

Example flow:
1. User calls `review` with files → creates thread, returns continuation_id
2. User continues with `chat` + continuation_id → full context preserved
3. Multiple tools can collaborate using same thread ID

## Development Setup

### Prerequisites

- Python 3.9+
- Virtual environment (managed via `.pal_venv/`)

### Installation

```bash
git clone <repo-url> pal-steamline
cd pal-steamline
python -m venv .pal_venv
source .pal_venv/bin/activate  # On Windows: .pal_venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

All configuration is via `.env`. Key variables:

```env
# Model routing
DEFAULT_MODEL=mimo
EXPERT_MODEL=gemini

# Custom API (primary provider)
CUSTOM_API_URL=https://your-endpoint.com/v1
CUSTOM_API_KEY=your-key

# Mistral
MISTRAL_API_KEY=your-mistral-key

# OpenRouter (gemini, gpt)
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_ALLOWED_MODELS=google/gemini-3.1-pro-preview,openai/gpt-5.4

# Optional: disable tools
DISABLED_TOOLS=apilookup,consensus

# Optional: conversation settings
CONVERSATION_TIMEOUT_HOURS=24
MAX_CONVERSATION_TURNS=40
```

### Running the Server

```bash
source .pal_venv/bin/activate
./run-server.sh
```

For Claude Code integration, add to your MCP config:

```json
{
  "mcpServers": {
    "pal": {
      "command": "/absolute/path/to/.pal_venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Run `./run-server.sh -c` to generate exact paths for your system.

## Development Workflow

### Code Quality Checks

Run before every commit:

```bash
source .pal_venv/bin/activate
./code_quality_checks.sh
```

This runs:
1. **Ruff** — linting with auto-fix
2. **Black** — code formatting (120 char line limit)
3. **isort** — import sorting
4. **pytest** — unit tests (excluding integration tests)

All checks must pass 100% for CI/CD to succeed.

### Running Tests

```bash
# All unit tests (fast)
source .pal_venv/bin/activate
pytest tests/ -v -m "not integration"

# Specific test file
pytest tests/test_chat_simple.py -v

# With coverage
pytest tests/ -v -m "not integration" --cov=. --cov-report=html

# Integration tests (requires API keys)
./run_integration_tests.sh

# Simulator tests (multi-turn conversation validation)
python simulator_tests/communication_simulator_test.py --quick
python simulator_tests/communication_simulator_test.py --verbose
python simulator_tests/communication_simulator_test.py --individual test_basic_conversation
```

### Adding a New Tool

1. Create tool file in `tools/` (inherit from `SimpleTool` or `WorkflowTool`)
2. Define system prompt in `systemprompts/`
3. Register tool in `server.py` TOOLS dictionary
4. Add unit tests in `tests/`
5. Add simulator test in `simulator_tests/` for multi-turn behavior
6. Update documentation

Example tool structure (SimpleTool pattern):

```python
from tools.simple.base import SimpleTool
from pydantic import Field

class MyToolRequest(ToolRequest):
    prompt: str = Field(..., description="User's question")
    files: list[str] = Field(default_factory=list)

class MyTool(SimpleTool):
    def get_name(self) -> str:
        return "mytool"
    
    def get_description(self) -> str:
        return "Brief description for tool picker"
    
    def get_system_prompt(self) -> str:
        return MY_TOOL_PROMPT  # from systemprompts/
    
    def get_request_model(self):
        return MyToolRequest
    
    async def prepare_prompt(self, request: MyToolRequest) -> str:
        # Build prompt with file context
        return self.prepare_chat_style_prompt(request)
    
    def format_response(self, response: str, request: MyToolRequest, 
                       model_info: dict = None) -> str:
        # Format AI response for user
        return f"{response}\n\n---\n\nAGENT'S TURN: Continue with task."
```

### Adding a Provider

1. Create provider file in `providers/` (inherit from `BaseModelProvider`)
2. Add model registry in `providers/registries/`
3. Register provider in `server.py` `configure_providers()`
4. Add configuration to `.env.example`
5. Add unit tests in `tests/`
6. Update documentation

## Coding Conventions

### Style Guidelines

- **Python 3.9+** with type hints
- **Black** formatting (120 char line limit)
- **isort** for import sorting
- **Ruff** for linting (pycodestyle, pyflakes, bugbear, comprehension, pyupgrade)
- **snake_case** for modules, functions, variables
- **PascalCase** for classes
- Explicit type hints preferred over implicit

### Architecture Patterns

**SimpleTool Pattern**: Base class for single-turn tools (chat, thinkdeep)
- Inherit from `SimpleTool`
- Define request model with Pydantic
- Implement hook methods: `prepare_prompt()`, `format_response()`
- Automatic conversation continuation support

**WorkflowTool Pattern**: Base class for multi-step tools (review, consensus)
- Inherit from `WorkflowTool`
- Define workflow steps with system prompts
- Automatic expert validation pass
- Token budget management across steps

**Provider Pattern**: Base class for AI provider integrations
- Inherit from `BaseModelProvider`
- Implement `generate_response()` and `list_models()`
- Handle provider-specific authentication and error handling
- Register in `ModelProviderRegistry`

### Testing Patterns

**Unit Tests** (`tests/`):
- Mirror production module structure
- Name tests `test_<behavior>` or `Test<Feature>` classes
- Use pytest fixtures from `conftest.py`
- Mock external API calls with `mock_helpers.py`
- Test both success and error paths

**Simulator Tests** (`simulator_tests/`):
- Test multi-turn conversation flows
- Validate cross-tool continuation
- Test token budget management
- Use `communication_simulator_test.py` harness

### Conversation Management

The server implements stateless-to-stateful conversation bridging:

1. **Thread Creation**: First tool call creates `ThreadContext` with UUID
2. **Context Reconstruction**: Subsequent calls with `continuation_id` load full history
3. **Token Budgeting**: Intelligent prioritization (newest files first, chronological turns)
4. **Cross-Tool Handoff**: Any tool can continue any thread with full context

Key functions:
- `reconstruct_thread_context()` — loads conversation state
- `build_conversation_history()` — creates prompt context with token limits
- `add_turn()` — records new conversation turn
- `get_thread()` — retrieves thread from storage

### Error Handling

- Use `ToolExecutionError` for tool-specific errors
- Return structured `ToolOutput` with status and metadata
- Log errors with context (thread ID, model, files)
- Provide user-friendly error messages with recovery instructions

### Logging

- Use Python's `logging` module
- Log levels: DEBUG (development), INFO (production), WARNING, ERROR
- Logs written to `logs/mcp_server.log` (rotating, 20MB max)
- Activity log in `logs/mcp_activity.log` for monitoring
- Include context: tool name, model, thread ID, token usage

## Commit Guidelines

Follow Conventional Commits: `type(scope): summary`

Types:
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation only
- `style` — formatting, no code change
- `refactor` — code restructuring
- `perf` — performance improvement
- `test` — adding/updating tests
- `build` — build system changes
- `ci` — CI/CD changes
- `chore` — maintenance tasks

Examples:
```
feat(tools): add review_type filter to review tool
fix(providers): handle OpenRouter rate limits gracefully
docs(readme): update model routing table
test(simulator): add consensus workflow validation
```

## Pull Request Guidelines

PRs should include:
1. **Intent**: What problem does this solve?
2. **Validation**: What commands did you run to test?
3. **Configuration**: Any new env vars or tool toggles?
4. **Screenshots/Logs**: For user-visible changes
5. **Breaking Changes**: Clearly marked if any

Before submitting:
```bash
source .pal_venv/bin/activate
./code_quality_checks.sh  # Must pass 100%
```

## Security Guidelines

- **Never commit secrets**: Use `.env` for API keys
- **Validate file paths**: Always use absolute paths, check existence
- **Sanitize prompts**: Remove PII before logging
- **Token limits**: Enforce model-specific context windows
- **Path traversal**: Validate all file operations stay within workspace

## Common Tasks

### Add a new model alias

1. Edit `conf/openrouter_models.json` (or provider-specific config)
2. Add alias to model entry
3. Update `.env.example` if needed
4. Test with `listmodels` tool

### Disable a tool

Add to `.env`:
```env
DISABLED_TOOLS=apilookup,consensus
```

### Change default model

Edit `.env`:
```env
DEFAULT_MODEL=gemini
```

### Adjust conversation limits

Edit `.env`:
```env
CONVERSATION_TIMEOUT_HOURS=48
MAX_CONVERSATION_TURNS=60
```

### Debug conversation issues

Check logs:
```bash
tail -f logs/mcp_server.log
tail -f logs/mcp_activity.log
```

Look for `[CONVERSATION_DEBUG]` markers.

## Troubleshooting

### Server won't start

1. Check `.env` has valid API keys
2. Verify virtual environment: `source .pal_venv/bin/activate`
3. Check logs: `logs/mcp_server.log`
4. Validate Python version: `python --version` (3.9+)

### Tool execution fails

1. Check model availability: use `listmodels` tool
2. Verify file paths are absolute
3. Check token limits for large files
4. Review logs for specific error

### Conversation continuation fails

1. Check thread hasn't expired (default 24 hours)
2. Verify continuation_id is valid UUID
3. Check server wasn't restarted (in-memory storage)
4. Review `[CONVERSATION_DEBUG]` logs

### Tests failing

1. Run individual test: `pytest tests/test_name.py -v`
2. Check for missing dependencies: `pip install -r requirements-dev.txt`
3. Verify API keys for integration tests
4. Check logs for specific failures

## Resources

- **MCP Protocol**: https://modelcontextprotocol.io/
- **Upstream PAL**: https://github.com/ppl-ai/pal-mcp-server
- **Claude Code**: https://claude.ai/code
- **OpenRouter**: https://openrouter.ai/
- **Mistral**: https://mistral.ai/

## GitHub CLI Commands

The GitHub CLI (`gh`) streamlines issue and PR management:

### Viewing Issues
```bash
gh issue view <issue-number>
gh issue view <issue-number> --comments
gh issue view <issue-number> --json title,body,author,state,labels,comments
gh issue view <issue-number> --web
```

### Managing Issues
```bash
gh issue list
gh issue list --label bug --state open
gh issue create --title "Issue title" --body "Description"
gh issue close <issue-number>
gh issue reopen <issue-number>
```

### Pull Request Operations
```bash
gh pr view <pr-number>
gh pr list
gh pr create --title "PR title" --body "Description"
gh pr checkout <pr-number>
gh pr merge <pr-number>
```

Install: `brew install gh` (macOS) or visit https://cli.github.com
