Status: done

# Issue 01: Job-aware Subtitle Scheduler

## What to build

Replace the single global subtitle-pipeline state with an in-memory Subtitle Queue that processes one identified Subtitle Job at a time. The existing main-screen subtitle-generation journey must continue to work, but its progress, completion result, and errors must be scoped to the job that started them.

The scheduler must reject a duplicate active or waiting job for the same Video and Source Language–Target Language pair, and it must use the Subtitle Cache rather than enqueueing external work when matching Cues already exist. A failed job must not stop the next job.

## Acceptance criteria

- [x] Each Subtitle Job has a stable identifier and exposes its own language pair, status, progress, result, and error through the application bridge.
- [x] Exactly one job is processed at a time in first-in, first-out order; the next waiting job starts after completion or failure.
- [x] Existing main-screen subtitle generation displays updates and Cues only for its own job, rather than a global pipeline result.
- [x] A duplicate active or waiting job for the same Video and language pair is rejected with a clear result.
- [x] A matching Subtitle Cache entry completes without external processing.
- [x] Backend and frontend integration tests cover sequential execution, job isolation, cache hits, duplicate rejection, and failure continuation.

## Blocked by

None - can start immediately.

## Comments

Implemented `SubtitleJobScheduler` with job-specific bridge events and isolated state. Verified: `uv run pytest -q`, `pnpm test`, `pnpm build`.
