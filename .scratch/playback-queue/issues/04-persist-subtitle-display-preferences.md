Status: done

# Issue 04: Persist Subtitle Display Preferences

## What to build

Keep the existing player-level subtitle controls separate from Subtitle Job creation. The video overlay continues to show one primary line—Original Subtitle or Translated Subtitle—while the Aa panel presents both lines and lets the viewer choose the primary line, hide or show individual lines, and adjust each font size.

Persist these application-wide Subtitle Display Preferences and restore them after relaunching the application. The Sub control must still hide or restore the video overlay without removing access to the Aa panel.

## Acceptance criteria

- [ ] The player retains the existing Sub and Aa controls, including the one-line overlay and both Original Subtitle and Translated Subtitle in the Aa panel.
- [ ] The viewer can choose the primary overlay line, change visibility of each available line, and set each line's font size.
- [ ] Subtitle Display Preferences are saved and restored across application launches.
- [ ] The Sub control hides and restores the overlay without losing access to the display controls.
- [ ] Tests cover persistence and restoration of the display choices, in addition to existing display interactions.

## Blocked by

- .scratch/playback-queue/issues/01-persisted-playback-queue-and-import.md
