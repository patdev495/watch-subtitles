# ADR 0005: TypeScript-only Frontend

## Status

Accepted

## Context

The frontend uses Vue 3 + TypeScript scaffolded via Vite. All existing `.vue` files already use `<script setup lang="ts">`. The alternative — allowing JavaScript via `allowJs: true` with optional `checkJs` — provides weaker guarantees: JS files bypass the type system by default and require per-file opt-in annotations.

## Decision

All frontend code must be written in TypeScript. No `.js` files are permitted in the `frontend/` directory. All Vue `<script>` blocks must declare `lang="ts"`. The TypeScript compiler enforces this at the build level via `"allowJs": false` in `tsconfig.app.json`.

## Consequences

- `pnpm build` (`vue-tsc -b && vite build`) will fail if any `.js` file is added or any `<script>` block omits `lang="ts"`.
- Agents and developers get immediate compiler feedback rather than silent type erosion.
- Migrating any future dependency that ships only CommonJS `.js` files must go through a `.d.ts` declaration file, not by relaxing `allowJs`.
