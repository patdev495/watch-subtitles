Status: done

# Issue 02: Two-Column Playback Workspace

## What to build

Make the Playback Queue the permanent left column of the player workspace, approximately 320 px wide with independent scrolling, and keep the media player in the remaining right column. Selecting a queue row loads and starts that Video, and clearly marks it as active. A row displays its Source Language, Subtitle Availability, and any current Subtitle Job progress.

Allow a user to remove a Video from the Playback Queue without cancelling any Subtitle Jobs. Removing the active Video stops it and selects the next Video, or empties the player if none remains. With Auto-advance enabled, playback moves to the next Video on completion, skipping files that cannot be played; failed files remain in the queue and show an error. Fullscreen continues to apply to the player only, hiding the queue naturally.

The player must load the most recently created cached subtitle pair as Active Subtitles; a Video with no cache has no subtitles.

## Acceptance criteria

- [x] The main workspace shows a scrollable ~320 px Playback Queue beside the player, with the active row visually distinct.
- [x] Selecting a row loads and starts its Video, and each row exposes Source Language, Subtitle Availability, job progress when applicable, and a separate remove action.
- [x] Removing the active Video stops it and chooses the next queued Video, or clears the player when the queue is empty, without cancelling its Subtitle Jobs.
- [x] Auto-advance moves to the next playable Video when enabled and skips unplayable entries while retaining and marking them in the queue.
- [x] Fullscreen contains only the player, as before.
- [x] The player uses the most recently created cached pair as Active Subtitles, or shows none when no cached pair exists.
- [x] Component and integration tests cover selection, removal, auto-advance, play failures, subtitle selection, and fullscreen behavior.

## Blocked by

- .scratch/playback-queue/issues/01-persisted-playback-queue-and-import.md
