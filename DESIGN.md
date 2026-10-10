# Watch Subtitles UI design

## Direction

Quiet, video-first desktop tool. The video fills the available player region; surrounding UI uses flat dark neutral surfaces. Existing Vietnamese copy, props, emits, playback and subtitle behavior remain intact.

## Tokens

The implementation source of truth is `frontend/src/theme.css`. Components use variables from that file.

| Role | Value |
| --- | --- |
| App / surface / hover / selected | `#0E0F12` / `#15171C` / `#1C1F26` / `#222632` |
| Border | `#23262F`, reserved for major divisions and fields |
| Primary / secondary / tertiary text | `#E8EAF0` / `#9BA1B0` / `#5F6677` |
| Accent | `#5B8CFF`, only primary action, progress and selection indicator |
| Success / danger | `#4CC38A` for ready dot / `#F26D6D` for destructive hover |
| Player / caption / overlay | `#000` / black at 65% / black at 60% |

Inter with `system-ui` fallback. Text sizes: 12px meta, 13px body, 14px file, 16px title. Weights: 400, 500, 600. Times use tabular numerals. Spacing follows a 4px scale; radii are 6px for controls and 8px for panels. Lucide icons use 1.5 stroke, 16px or 18px. Motion is 120–160ms ease-out for color, background and opacity, with reduced-motion support.

## Layout

- Header: 48px, surface background and bottom divider. Video context left; subtitle ghost, single primary open-video button, settings icon and ready status right.
- Workspace: 264px fixed library sidebar plus flexible player. At 900×600 and 1920×1080 the player keeps its available area without overflow.
- Library: flat rows near 52px with filename and cached language pairs; active row has selected fill and a 2px accent indicator. Remove button appears on hover or keyboard focus. Import, clear and auto-advance controls remain in the sidebar header.
- Player: black letterbox, no frame or shadow. Overlay controls sit at the bottom and hide during idle playback. Captions clear the controls. Subtitle tools live in the upper right and hide with the controls.
- Dialogs and cue details: floating 8px panels, one shadow, no decorative effects.

## Components and states

| Component | States |
| --- | --- |
| HeaderBar | video selected/empty, cached/uncached, connected/disconnected, hover, focus, disabled |
| PlaybackQueue | empty, rows, selected, cached language pairs, generating, error, hover/focus removal |
| VideoPlayer / PlayerControls | empty, playing, paused, idle controls, hover, fullscreen, seek, volume, speed |
| TranscriptFooter | hidden/visible subtitles, active cue, detail panel, display settings, export feedback |
| SubtitleGenerationModal | empty, waiting, processing, complete, failed, retry, disabled |
| SettingsModal | editing, testing, saving, success/error, disabled |
| App notifications | completion/error toast, dismissible |

Every interactive control has hover, focus-visible and disabled treatment. Focus uses a 2px accent outline with 2px offset. Loading uses a small spinner or progress line. Error feedback is a compact lower-right toast.

## Anti-patterns

No purple/navy palette, decorative gradient, glow, glass blur, nested cards, per-row borders, repeated library dropdown, mixed icon sets, unexplained icon buttons, or component-local hardcoded design values. Use at most three text tones in one area. Keep the header to one filled accent button.
