Status: done

# Issue 02: Queue Screen for Single-Video Generation

## What to build

Add a dedicated Queue Screen that manages Queued Videos without changing the Video selected for playback on the main screen. The user can add one Video at a time, then request subtitle generation for an individual Queued Video.

Generation must create a Subtitle Job using the Source Language and Target Language selected at that moment. The Queue Screen must show that job's progress and terminal state while the main Video continues to play unchanged. Completion and failure must display small, dismissible-or-auto-hiding notifications, while the Queue Screen keeps the corresponding Queued Video and its status visible for the rest of the application session.

## Acceptance criteria

- [x] The app provides a Queue Screen separate from the playback screen.
- [x] A user can add exactly one Video per add action without replacing or changing the Video currently playing.
- [x] A user can start subtitle generation for one Queued Video, and the resulting Subtitle Job uses the language pair selected when that action occurred.
- [x] The Queue Screen shows waiting, processing, completed, and failed job states scoped to each Video and language pair.
- [x] A completed or failed Queued Video remains visible until the user removes it or closes the application; a running job cannot be removed.
- [x] Completion or failure notifications do not replace the current playback Video or its displayed Cues.
- [x] End-to-end UI and bridge tests cover adding a Video, starting its job, observing progress, and preserving playback selection.

## Blocked by

- .scratch/subtitle-queue/issues/01-job-aware-subtitle-scheduler.md

## Comments

Implemented Queue Screen, per-video job states, bridge-driven updates, and dismissible auto-hiding terminal notifications. Verified via Vue component/bridge integration tests, `pnpm test`, and `pnpm build`.
