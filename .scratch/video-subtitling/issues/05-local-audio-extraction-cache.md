Status: ready-for-agent

# Issue 05: Local Audio Extraction & Video Fingerprint Cache

## Parent
.scratch/video-subtitling/PRD.md

## What to build
Implement media preprocessing and local subtitle caching in the Python backend.

1. **Video Fingerprint**: Compute a deterministic content hash of the input video file (sampling header, tail, and file size) so videos can be identified even if renamed or moved to another folder.
2. **Audio Extraction**: Use local FFmpeg (invoked safely via Python subprocess) to extract the audio stream from the video into an optimized mono/16kHz compressed audio format (`.mp3` or `.wav`) in a temporary directory.
3. **Subtitle Cache**: Maintain a local persistent store (SQLite database or JSON store keyed by `Video Fingerprint`) capable of storing and querying previously generated `Cue` sequences along with their Target Language.

## Acceptance criteria
- [ ] Deterministic `Video Fingerprint` function returns identical hashes for the same file when renamed or moved, but distinct hashes for different media files.
- [ ] FFmpeg audio extraction module reliably isolates audio from supported video containers without freezing the UI thread.
- [ ] Cache database schema stores `video_fingerprint`, `source_filename`, `target_language`, and serialized `cues`.
- [ ] Querying the cache for a cached video returns existing cues immediately without requiring audio extraction or external API calls.
- [ ] Unit tests verify fingerprint calculation and cache read/write operations.

## Blocked by
.scratch/video-subtitling/issues/02-local-video-loading-playback.md
