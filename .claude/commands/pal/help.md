Output the following block exactly as written, with no additions, omissions, or rephrasing:

---

## PAL Tools

| I want to... | Tool | Notes |
|---|---|---|
| Ask a model a question | `chat` | General Q&A, code, explanations, analysis |
| Reason through something hard | `thinkdeep` | Multi-step investigation; accepts `continuation_id` from chat |
| Figure out why something's broken | `debug` | Steps through the problem, tests theories, finds the root cause |
| Check if my code is solid | `review` | Spots bugs, security holes, and performance issues — for code that works |
| Clean up messy code | `cleanup` | Reorganizes, simplifies, and modernizes without changing behavior |
| Get multiple models to weigh in | `consensus` | Collects perspectives from 2–3 models |

Workflow tools (`thinkdeep`, `debug`, `review`, `consensus`) are multi-step — they return a `continuation_id`. Pass it back to continue the thread.

**Model aliases:** `mimo` (default) · `gemini` · `gpt` · `qwen` · `mistral`

If no model is specified, `mimo` is used.
