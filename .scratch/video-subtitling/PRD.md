# PRD: Video Subtitling & Playback Desktop Application

## Overview
A desktop application that allows users to play local video files with automated speech-to-text (STT) transcription and external translation. Bilingual subtitles (original spoken language + target translated language) are presented synchronously in an Interactive Transcript Footer with click-to-seek playback.

## Architecture & Tech Stack
- **Platform**: Desktop Application via `pywebview`.
- **Frontend**: Vue 3 + Vite + TypeScript, package managed via `pnpm`.
- **Backend**: Python 3.12+ with strict typing (Pydantic / type annotations), managed via `uv`.
- **External APIs**: Deepgram (Speech-to-Text) & DeepL (Translation) using Bring-Your-Own-Key (BYOK).
- **Media Engine**: Local FFmpeg for audio extraction and format conversion.
- **Cache**: Subtitle Cache keyed by deterministic `Video Fingerprint` (chunk content hash) to avoid duplicate API expenses.

## Core User Journey
1. **Load Video**: User opens or drags a video into the app.
2. **Process Subtitles**: User selects target language and clicks "Process". If the video's fingerprint exists in the local Subtitle Cache, subtitles load immediately. Otherwise, FFmpeg extracts audio locally, sends it to Deepgram for STT, translates text via DeepL, stores the result in cache, and populates the player.
3. **Bilingual Playback**: Video plays while the Interactive Transcript Footer highlights the active bilingual cue in real-time and auto-scrolls. Clicking any cue jumps playback to that moment.
4. **Export**: User can export synchronized bilingual subtitles as `.srt` or `.vtt`.

## Implementation Issues
- `01-project-skeleton-desktop-shell.md`
- `02-local-video-loading-playback.md`
- `03-interactive-transcript-footer.md`
- `04-api-key-settings-persistence.md`
- `05-local-audio-extraction-cache.md`
- `06-stt-translation-pipeline.md`
- `07-bilingual-subtitle-export.md`
