Status: done

# Issue 03: Interactive Transcript Footer

## Parent
.scratch/video-subtitling/PRD.md

## What to build
Build the `Interactive Transcript Footer` component in Vue 3 that displays synchronized bilingual subtitle cues (Original Subtitle and Translated Subtitle) docked at the bottom of the playback interface.

The component accepts a reactive list of strongly-typed `Cue` items:
```typescript
interface Cue {
  id: string;
  start: number; // in seconds
  end: number;   // in seconds
  originalText: string;
  translatedText: string;
}
```

During playback, as the video emits time updates, the footer highlights the active cue's `Bilingual Display` and smoothly auto-scrolls the active cue into visible range. If the user clicks on any cue in the transcript, the video immediately seeks to that cue's start timestamp.

Includes mock data fixtures to test and verify the component independently before backend STT/Translation are wired up.

## Acceptance criteria
- [x] TypeScript definition for `Cue` model defined in shared types.
- [x] Footer renders all cues with dual text (original on top, translated below) with clean typography.
- [x] Active cue dynamically highlights when `videoCurrentTime` falls within `[start, end]`.
- [x] Footer container auto-scrolls to keep the active cue centered or visible without jarring user interaction.
- [x] Clicking any cue dispatches a seek event to the video player and updates playback to that cue's start timestamp.
- [x] Tested and verified using a mock list of 50+ cues.

## Blocked by
.scratch/video-subtitling/issues/02-local-video-loading-playback.md
