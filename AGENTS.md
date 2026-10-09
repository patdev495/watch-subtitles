# AGENTS.md

## Project Overview

Repository: `watch-subtitles`
Remote: `https://github.com/patdev495/watch-subtitles.git`

## Environment & Engineering Rules

- Python Backend: UV ONLY (`uv run python`, `uv add`, `uv sync`). Never use `pip` or plain `python`. Enforce strict type annotations / Pydantic models.
- Frontend: PNPM ONLY (`pnpm install`, `pnpm dev`, `pnpm build`). Vue 3 + TypeScript with full type checking (`vue-tsc`).
- Architecture: Maintain loose coupling, separate UI, business logic, and infrastructure.

## Agent skills

### Issue tracker

Local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles plus `done` for completed issues. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`CONTEXT.md` and `docs/adr/` at root). See `docs/agents/domain.md`.
