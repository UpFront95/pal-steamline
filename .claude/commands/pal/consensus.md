Start a PAL consensus workflow on: $ARGUMENTS

Call `mcp__pal__consensus` with at least two models. Default to `[{"model": "mimo", "stance": "neutral"}, {"model": "gemini", "stance": "for"}, {"model": "gpt", "stance": "against"}]` unless the user specifies models or stances.

Each entry supports:
- `model`: alias (mimo, gemini, gpt)
- `stance`: `for` · `against` · `neutral` (default)

This is a multi-step workflow that returns a `continuation_id`. Pass it back to continue the thread.
