# Watch Subtitles UI design

## Direction

A calm, layered desktop player: a cinema-framed video stage on a deep neutral canvas, a thumbnail library beside it, and a single teal accent reserved for the one action that matters on each surface. Teal (`#14B8A6`) marks primary actions, the playing row, progress, focus rings, and "in progress" states — nothing else. Four surface levels (`--bg-base` → `--bg-surface` → `--bg-raised` → `--bg-hover`) separate the canvas, panels, cards and fields so the interface reads as layers rather than one flat grey.

Both a **dark** (default) and a **light** theme ship from the same token names. The header toggle flips `data-theme` on `<html>`, and the choice is persisted through the bridge (`get_theme` / `save_theme`) with a `localStorage` fallback so plain `pnpm dev` keeps working. The player stage and caption overlay stay dark in both themes: they sit on top of video, where a light surface would wash the picture out.

Existing Vietnamese copy, props, emits, playback and subtitle behavior remain intact.

## Tokens

`frontend/src/theme.css` is the source of truth; everything else consumes its variables. Light overrides only redefine the same names under `:root[data-theme='light']`.

| Role | Dark (default) | Light |
| --- | --- | --- |
| Canvas / surface / raised / hover / active | `#0b0e14` / `#14171f` / `#1a1f2b` / `#222836` / `#2a3142` | `#f4f6f8` / `#ffffff` / `#f8fafb` / `#eef3f6` / `#e4ecf0` |
| Border subtle / strong | `#232a38` / `#333c4e` | `#e2e8ed` / `#c9d4dc` |
| Text primary / secondary / muted | `#edf1f7` / `#a3afc2` / `#6b7688` | `#0f1720` / `#4a5a66` / `#6e8090` |
| Accent / hover / soft / on-accent text | `#14b8a6` / `#2dd4bf` / `rgba(20,184,166,.14)` / `#04211e` | `#0f766e` / `#115e59` / `rgba(15,118,110,.10)` / `#ffffff` |
| Success / warning / danger | `#22c55e` / `#f59e0b` / `#f04438` | `#15803d` / `#b45309` / `#dc2626` |
| Player stage / caption | `#000` (both themes) | `#000` (both themes) |

Accent text on accent fill must use `--accent-contrast`, never white on the dark theme's teal (that pairing is only ~2.5:1).

Inter with a `system-ui` fallback. Sizes: 12px meta, 14px body, 15px file, 18px title, 22px display, 26px hero; weights 400/500/600. Times and counters use tabular numerals. Spacing follows a 4px scale; radii are 8px (small), 10px (controls), 14px (cards), 18px (panels/stage). Lucide icons use 1.5 stroke at 16–22px. Motion is 140ms ease-out for color/background and 200ms cubic-bezier(0.2, 0.8, 0.2, 1) for panels, with reduced-motion support.

## Layout

- **Header (56px)**: brand mark and wordmark (wordmark hides under 1080px), hairline divider, then the current Video with its subtitle-availability dot. Actions, left to right: backend status dot, theme toggle, settings, "Phụ đề" ghost button, and the single accent "Mở video" button.
- **Workspace**: 340px library sidebar plus a flexible player whose stage floats inside a padded canvas.
- **Library (PlaybackQueue)**: rows of a 104×58 thumbnail, filename, language-pair badges and a job chip (spinner + `%`, or "Đang chờ") with a progress bar along the thumbnail's bottom edge. Thumbnails come from `get_thumbnail_url` and degrade to a gradient tile with a film icon (no bridge, no FFmpeg, or a failed image). The playing row carries an accent tint, accent border, left indicator and a play overlay. Import/clear live in the sidebar header; "Tự chuyển video" is pinned in the sidebar footer. Empty state offers a direct "Chọn video" action.
- **Player**: the stage is a 16px-radius black frame with hairline border and layered shadow; the transport dock sits below it and only becomes a scrim overlay (auto-hiding while playing) in fullscreen. Empty state is a dashed drop zone with icon, title, hint and an "Mở video" button.
- **Transport (PlayerControls)**: full-width timeline row with current/total time at the ends (6px track, 9px on hover, accent fill and thumb), then a 44px button row — previous, −10s, a 50px round accent play/pause, +10s, next — with volume, speed and fullscreen on the right. Queue-hopping buttons disable at the ends of the Playback Queue.
- **Captions and cue drawer**: bilingual caption pills stay dark and blurred over the video in both themes; the toolbar pill follows the controls-visibility rule; the cue drawer follows the active theme.
- **Dialogs**: 18px panels on a blurred backdrop, header with an accent icon chip, section cards in the body, sticky footer. Subtitle jobs render as cards with tone-coloured state chips (waiting amber, processing accent, cached green, failed red) and a progress bar while running.

## Components and states

| Component | States |
| --- | --- |
| HeaderBar | video selected/empty, cached/uncached, connected/disconnected, dark/light theme, hover, focus, disabled |
| PlaybackQueue | empty, rows, playing, cached language pairs, thumbnail fallback, generating, failed, hover/focus removal |
| VideoPlayer / PlayerControls | empty, playing, paused, idle in fullscreen, hover, seek, volume, speed, queue ends |
| TranscriptFooter | subtitles hidden/visible, active cue, detail panel, display settings, export feedback |
| SubtitleGenerationModal | empty, waiting, processing, complete, failed, retry, disabled |
| SettingsModal | editing, testing, saving, success/error, disabled |
| App notifications | completion/error toast, dismissible |

Every interactive control has hover, focus-visible (2px accent outline) and disabled treatment. Errors surface as a compact lower-right toast with a coloured edge.

## Anti-patterns

No decorative gradients, rainbow palettes, coloured neon glows, or second accent colours competing with teal. No single-tone grey where three surface levels are needed. Keep video and subtitle content the most prominent thing on screen.
