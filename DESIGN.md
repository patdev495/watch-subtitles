# Watch Subtitles UI design

## Direction

Titanium Zinc Monochrome desktop pro tool (macOS & Vercel engineering aesthetic). The video fills the available player region; surrounding UI uses tactile, neutral Zinc charcoal surfaces (`#101012`, `#18181b`) with crisp hairline borders, stark white typography, and solid high-contrast monochrome controls. Zero purple/navy tint, zero decorative gradients, and zero artificial neon glow. Existing Vietnamese copy, props, emits, playback and subtitle behavior remain intact.

## Tokens

The implementation source of truth is `frontend/src/theme.css`. Components use variables from that file.

| Role | Value |
| --- | --- |
| App / surface / hover / selected | `#101012` / `#18181b` / `#222226` / `#2a2a30` |
| Border | `#27272a` (hairline subtle), `#3f3f46` (strong division) |
| Primary / secondary / tertiary text | `#fafafa` / `#a1a1aa` / `#71717a` |
| Primary action / accent | `#ffffff` (stark white solid with `#09090b` text) |
| Success / danger | `#22c55e` (emerald dot) / `#ef4444` (destructive hover) |
| Player / caption / overlay | `#000` / `rgba(20, 20, 24, 0.86)` / `rgba(18, 18, 20, 0.82)` |

Inter with `system-ui` fallback. Text sizes: 12px meta, 13px body, 14px file, 16px title. Weights: 400, 500, 600. Times use tabular numerals. Spacing follows a 4px scale; radii are 7px for controls and 10px for panels/modals. Lucide icons use 1.5 stroke, 16px or 18px. Motion is 140ms ease-out for color, background, and opacity, with reduced-motion support.

## Layout

- Header: 48px, solid zinc surface (`#18181b`) and bottom hairline divider (`#27272a`). Video context left; subtitle ghost, single primary stark-white open-video button, settings icon and ready status right.
- Workspace: 264px fixed library sidebar plus flexible player. At 900×600 and 1920×1080 the player keeps its available area without overflow.
- Library (PlaybackQueue): zinc rows near 52px with filename, neutral pill language badges, and minimal job indicators; active row has selected fill and white indicator. Remove button appears on hover or keyboard focus. Import, clear and auto-advance toggle remain in the sidebar header.
- Player: black letterbox. Overlay controls float seamlessly at the bottom and hide during idle playback. Bilingual captions render as clean dark matte pills with high-legibility text shadows. Subtitle tools live in the upper right.
- Dialogs and cue details: floating 10px panels with dark matte backdrop, crisp hairline border, and diffused layered shadow.

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

Every interactive control has hover, focus-visible and disabled treatment. Focus uses a 2px stark white outline with 2px offset. Loading uses a small neutral spinner. Error feedback is a compact lower-right toast.

## Anti-patterns

No purple or navy tints, no decorative rainbow or button gradients, no colored neon glow shadows, no unstyled native HTML form elements, and no AI-generated glass template clichés. Keep surfaces neutral, tactile, and restrained so video and subtitle content remain the primary focus.
