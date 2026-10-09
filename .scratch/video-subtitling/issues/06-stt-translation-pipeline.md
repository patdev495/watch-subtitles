Status: done

# Issue 06: STT & Translation Pipeline with Progress Bar

## Parent
.scratch/video-subtitling/PRD.md

## What to build
Build the complete automated subtitling pipeline connecting video input, audio extraction, external API transcription, external translation, and playback delivery.

1. User selects a Target Language and clicks "Generate Subtitles" / "Tạo phụ đề".
2. If already in `Subtitle Cache` for that target language, cues load instantly into the footer.
3. Otherwise, the app initiates the pipeline:
   - Stage 1: Extract Audio Track locally (0% - 20%).
   - Stage 2: Send audio to Deepgram Speech-to-Text API to receive timestamped utterances/words (20% - 60%).
   - Stage 3: Send original text cues to DeepL Translation API in batches to receive target language translations (60% - 90%).
   - Stage 4: Assemble finalized `Cue` objects, write to `Subtitle Cache`, and return to frontend (90% - 100%).
4. The Vue UI displays a clear step-by-step progress bar and status text throughout processing.
5. Once complete, cues are automatically injected into the `Interactive Transcript Footer` and playback is ready.

## Acceptance criteria
- [ ] Abstract `TranscriptionProvider` interface with Deepgram implementation supporting utterance-level timestamps.
- [ ] Abstract `TranslationProvider` interface with DeepL implementation preserving sentence boundaries.
- [ ] Backend runs pipeline asynchronously in a background thread to prevent blocking the `pywebview` UI.
- [ ] Real-time progress updates (percentage + step label) are reported to the Vue frontend.
- [ ] Finished cues are persisted in the `Subtitle Cache` and loaded into the `Interactive Transcript Footer`.
- [ ] Graceful error handling (e.g. invalid API key, no internet, FFmpeg failure) surfaces clear toast/modal alerts to the user.

## Blocked by
- .scratch/video-subtitling/issues/03-interactive-transcript-footer.md
- .scratch/video-subtitling/issues/04-api-key-settings-persistence.md
- .scratch/video-subtitling/issues/05-local-audio-extraction-cache.md
