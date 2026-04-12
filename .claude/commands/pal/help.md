Output the following block exactly as written, with no additions, omissions, or rephrasing:

---

## PAL Tools

| I want to... | Tool | Notes |
|---|---|---|
| Ask another model a question | `chat` | General Q&A, code, explanations, analysis |
| Reason through something hard | `thinkdeep` | Multi-step investigation; accepts `continuation_id` from a chat thread |
| Debug a specific issue | `debug` | Systematic hypothesis-driven debugging |
| Audit code for quality/security/perf | `codereview` | Quality, security, and performance audit |
| Restructure or clean up code | `refactor` | Types: `codesmells` (default), `decompose`, `modernize`, `organization` |
| Get multiple models to weigh in | `consensus` | Collects perspectives from 2–3 models |

Workflow tools (`thinkdeep`, `debug`, `codereview`, `consensus`) are multi-step — they return a `continuation_id`. Pass it back to continue the thread.

**Model aliases:** `mimo` (default) · `gemini` · `gpt` · `qwen` · `mistral`

If no model is specified, `mimo` is used.
