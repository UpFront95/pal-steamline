Start a PAL consensus workflow on: $ARGUMENTS

Call `mcp__pal__consensus` with at least two models. Default to `[{"model": "mimo-v2.5-pro"}, {"model": "gemini"}]` unless the user specifies models or stances.

Each entry supports:
- `model`: alias (mimo-v2.5-pro, gemini, gpt, qwen)
- `stance`: `for` · `against` · `neutral` (default)

This is a multi-step workflow that returns a `continuation_id`. Pass it back to continue the thread.
