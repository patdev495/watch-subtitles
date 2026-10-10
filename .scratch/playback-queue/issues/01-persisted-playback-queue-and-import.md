Status: done

# Issue 01: Persisted Playback Queue and Queue Import

## What to build

Replace the session-only collection of Queued Videos with a persisted Playback Queue. A user can add multiple Video files in one action or import all supported Video files directly inside a selected folder. New unique Videos append to the queue; multi-file selection keeps the selected order and folder import sorts by filename A–Z. Duplicate additions are ignored and report “Video đã trong hàng đợi rồi.”

Persist the Playback Queue, selected Video, last playback time, per-Video Source Language assignment, and Auto-advance preference through the existing application settings store. Restore that state at application start, omitting unavailable file paths. Auto-advance is enabled on first use, then retains the user's saved choice.

## Acceptance criteria

- [x] The user can import multiple Video files or the supported Video files directly inside one folder; folder import does not scan subfolders.
- [x] Import appends unique Videos in the specified order and reports the Vietnamese duplicate message without adding a second entry.
- [x] Playback Queue state is restored after restarting the application, including order, selected Video, its last playback time, each Video's Source Language assignment, and Auto-advance preference.
- [x] Missing paths are omitted safely during restoration.
- [x] First-use Auto-advance defaults to enabled; later launches restore the saved value.
- [x] Bridge, backend, and frontend tests cover importing, duplicate handling, state persistence, and restoration with missing paths.

## Blocked by

None - can start immediately.
