Status: ready-for-agent

# Issue 04: API Key Settings & Persistence

## Parent
.scratch/video-subtitling/PRD.md

## What to build
Provide a Settings dialog in the Vue frontend where users can enter and manage their external service credentials (Deepgram API Key for STT, DeepL API Key for Translation) and default Target Language (e.g. Vietnamese, English, Japanese, French).

The Python backend securely stores these preferences in a local JSON or SQLite configuration file in the user's application data directory. Upon launching the application, saved settings are retrieved and populated into the UI state.

## Acceptance criteria
- [ ] Pydantic model on backend defining `AppSettings` (deepgram_api_key, deepl_api_key, default_target_language).
- [ ] Settings modal in Vue accessible via a gear icon with form validation.
- [ ] Backend bridge exposes `get_settings()` and `save_settings(settings: AppSettings)` methods.
- [ ] API keys are persisted across application restarts.
- [ ] Includes an optional "Test Connection" button that validates the entered Deepgram and DeepL API keys by sending lightweight test ping requests.

## Blocked by
.scratch/video-subtitling/issues/01-project-skeleton-desktop-shell.md
