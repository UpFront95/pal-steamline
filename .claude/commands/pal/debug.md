Start a PAL debug workflow on: $ARGUMENTS

Call `mcp__pal__debug` with `model="mimo"` and the user's prompt. Pass any relevant file paths as `absolute_file_paths`.

`confidence` levels: `exploring` · `low` · `medium` · `high` · `very_high` · `almost_certain` · `certain`
Default to `exploring` when starting. Use `certain` only when root cause and fix are both locally confirmed.

This is a multi-step workflow that returns a `continuation_id`. Pass it back to continue the thread.
