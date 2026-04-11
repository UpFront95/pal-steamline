# Global CLAUDE.md Setup

Claude Code loads `~/.claude/CLAUDE.md` automatically in every project session, before any project-level `CLAUDE.md`. Use it to give Claude standing instructions about PAL so you don't have to repeat yourself.

## Recommended content

```markdown
# PAL MCP Tools

**Never invoke pal tools unless the user explicitly asks.**
**Never call a model that isn't explicitly aliased. Available aliases: `mimo` (default), `gemini`, `gpt`, `qwen`.**

## Responding to "pal, how can you help?" (or similar)

List the operational tools and available model aliases:

**Tools:**
- `chat` — ask a model a question, get code, explanations, analysis
- `thinkdeep` — extended reasoning on hard problems
- `debug` — systematic multi-step debugging workflow
- `codereview` — code review (`mode="review"`) or refactor analysis (`mode="refactor"`)
- `consensus` — get multiple models to weigh in on a question

**Model aliases:** `mimo` (default), `gemini`, `gpt`, `qwen`

## Tool picker

| I want to... | Tool |
|---|---|
| Ask another model a question | `chat` |
| Reason through something hard | `thinkdeep` |
| Debug a specific issue | `debug` |
| Review or refactor code | `codereview` |
| Get multiple models to weigh in | `consensus` |

## Invocation notes

- Workflow tools (`debug`, `codereview`, `thinkdeep`, `consensus`) are multi-step — they return a `continuation_id`. Pass it back to continue.
- If the user doesn't specify a model, use `mimo`.
```

## How to install

```bash
mkdir -p ~/.claude
cat > ~/.claude/CLAUDE.md << 'EOF'
# PAL MCP Tools
... paste the content above ...
EOF
```

## What it does

- Prevents Claude from calling PAL tools unsolicited
- Prevents Claude from using unaliased model names (which would fail at runtime)
- Gives Claude a ready answer when you ask "pal, how can you help?"
- Reminds Claude to pass `continuation_id` back on multi-step tools

## Keeping it in sync

If you add or remove tools or aliases, update `~/.claude/CLAUDE.md` to match. The aliases must correspond to entries in `conf/openrouter_models.json` or `conf/custom_models.json`.
