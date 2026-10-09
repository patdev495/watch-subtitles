Status: done

# Issue 01: Project Skeleton & Desktop Shell

## Parent
.scratch/video-subtitling/PRD.md

## What to build
Scaffold the complete project structure with a Vue 3 + TypeScript frontend (managed by `pnpm`) and a Python backend (managed by `uv`). Establish a native desktop window using `pywebview` where the frontend can invoke a basic bridge API method on the Python backend (e.g. `ping()` -> `pong`) and receive typed responses.

Ensure both codebases have strict typing and linting configured (`vue-tsc` for TypeScript and `mypy`/type annotations for Python).

## Acceptance criteria
- [x] Python project initialized with `uv` (`pyproject.toml`) with dependencies including `pywebview` and type checking tools.
- [x] Frontend initialized with Vue 3, Vite, and TypeScript using `pnpm`.
- [x] Launching the Python entrypoint (`uv run python main.py` or script) spawns a desktop window rendering the Vue 3 app.
- [x] A test button in the UI triggers a Python backend method via the `pywebview` bridge and displays the response without errors.
- [x] Type checks pass cleanly (`pnpm run type-check` or `vue-tsc --noEmit`).

## Blocked by
None - can start immediately.
