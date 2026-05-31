Output the following block exactly as written, with no additions, omissions, or rephrasing:

---

## PAL Tools

| Tool | What it does |
|---|---|
| `chat` | Multi-turn chat — pass `continuation_id` back to continue the thread |
| `review` | Multi-step code review workflow — pass `continuation_id` back to advance each step |
| `consensus` | Consults 2+ models in sequence then synthesizes — pass `continuation_id` back to advance each step |
| `planreview` | Sends the most recent Claude Code plan to a PAL model for critical review |
| `listmodels` | Lists available models and aliases |

**Model aliases:** `mimo` (default) · `gemini` · `gpt`

## Options

- **`review`** — `review_type`: `full` (default) · `security` · `performance` · `quick`
- **`consensus`** — per-model `stance`: `for` · `against` · `neutral` (defaults to `neutral`)
