Status: done

# Issue 03: Subtitle Generation Modal for Playback Queue

## What to build

Replace the dedicated Queue Screen and header language-pair controls with a single “Phụ đề” action that opens the Subtitle Generation Modal. The modal lists Playback Queue Videos and permits a separately editable Source Language–Target Language pair for every row. A user can create one Subtitle Job, create all eligible jobs in Playback Queue order, or retry a failed job.

The modal must make existing Subtitle Availability explicit and skip cached pairs during “Create all.” It must prevent duplicate active work for a matching pair, show waiting, processing, completed/cache, and failed states, and remain optional while jobs run in the background. When reopened, it reflects current progress, while the matching Playback Queue row also reports progress. Removing a Video from Playback Queue must not cancel its queued or processing Subtitle Jobs.

## Acceptance criteria

- [ ] The header no longer exposes language-pair selectors, Queue Screen navigation, or direct subtitle-generation controls; it has one action that opens the Subtitle Generation Modal.
- [ ] Each modal row permits editing its Source Language and Target Language before creating a Subtitle Job.
- [ ] The user can create a job for one Video, create all eligible jobs in Playback Queue order, and retry a failed job with its original pair.
- [ ] “Create all” skips rows with Subtitle Availability for their selected pair and active matching jobs cannot be duplicated.
- [ ] Waiting, processing, completed/cache, and failed states are visible in the modal; background progress remains correct when the modal is closed and reopened.
- [ ] Matching job progress is visible in the Playback Queue, and queue removal never cancels the Video's Subtitle Jobs.
- [ ] Legacy Queue Screen code and its tests are replaced by modal-focused tests without regressing FIFO scheduler or cache behavior.

## Blocked by

- .scratch/playback-queue/issues/01-persisted-playback-queue-and-import.md
- .scratch/playback-queue/issues/02-two-column-playback-workspace.md
