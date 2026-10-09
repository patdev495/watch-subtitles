Status: done

# Issue 03: Batch Queue Controls and Retry

## What to build

Extend the Queue Screen so the user can request subtitle generation for all eligible Queued Videos, remove work that has not started, and retry a failed Subtitle Job. “Create subtitles for all” must create jobs in Queued Video order and let the Subtitle Queue process them sequentially.

Retrying creates a new job at the end of the Subtitle Queue using the failed job's original language pair. The Queue Screen must support multiple language-pair jobs for the same Video, while preventing duplicate active or waiting work for the same pair.

## Acceptance criteria

- [x] “Create subtitles for all” creates jobs for all eligible Queued Videos in their displayed order.
- [x] The scheduler processes batch-created jobs sequentially and does not disrupt main-screen playback.
- [x] A user can remove a waiting job; the UI does not offer removal for a running job.
- [x] A failed job offers a manual retry that keeps its original Source Language and Target Language and enters the end of the Subtitle Queue.
- [x] A Video can retain jobs for multiple language pairs, while a duplicate active or waiting pair remains prevented.
- [x] Cached Cues are used without new provider calls and are reflected clearly in Queue Screen status.
- [x] Tests cover batch ordering, removal of waiting work, retry placement, multiple language pairs, and cache behavior.

## Blocked by

- .scratch/subtitle-queue/issues/02-queue-screen-single-video-generation.md

## Comments

Implemented batch enqueue, waiting-job cancellation, language-pair-preserving retry, and cache state. Verified via scheduler and Queue Screen tests.
