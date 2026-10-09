# Desktop Technology Stack

We decided to use a hybrid desktop architecture combining a **Vue 3 + TypeScript** frontend (managed with `pnpm`) and a **Python** backend with strict type hints (managed via `uv`), packaged natively using `pywebview`.

The Vue 3 + TypeScript frontend (scaffolded with Vite) provides reactive state synchronization for video playback, accurate timestamp-based active cue detection, and smooth auto-scrolling for the bilingual subtitle footer. The Python backend (fully typed with Pydantic/dataclasses and type annotations) manages FFmpeg media operations, communicates with external APIs (Deepgram & DeepL), and handles local cache persistence. Both environments enforce full static typing for reliability and maintainability.
