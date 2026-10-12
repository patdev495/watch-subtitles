# Watch Subtitles UI design

## Direction

A simple desktop media player inspired by the clarity of Windows Media Player Legacy. The Video remains the main focus, with a compact Playback Queue beside it and a flat transport strip below it. The reference informs the visual hierarchy and density; the application keeps its own actions and does not add decorative media-library menus or tabs.

The interface uses a light theme by default, with a dark-theme toggle. Both themes share the same compact layout, thin dividers, small corner radii, neutral surfaces, and restrained blue accent. Blue is reserved for the selected Video, the main play action, progress, and keyboard focus. Other controls remain neutral. Avoid gradients, glass effects, prominent shadows, glossy controls, and decorative color. A subtle dialog shadow may separate a dialog from the workspace.

The video stage remains black in both themes. The existing subtitle overlay, Interactive Transcript Footer, cue detail, and subtitle display behavior remain as they are because they are already readable over video. Existing Vietnamese copy and playback, queue, and subtitle workflows remain intact.

## Layout

- **Header:** A compact toolbar with the current Video and the existing connection, theme, settings, subtitle, and open-video actions. Keep the actions easy to identify; do not reproduce Windows Media Player's library breadcrumbs, Play/Burn tabs, or unrelated menus.
- **Workspace:** A narrow Playback Queue on the side and the Video as the dominant region. Use thin dividers instead of floating panels and large shadows.
- **Playback Queue:** Use compact rows with smaller thumbnails, filenames, subtitle availability, and job progress. Avoid card-like rows. Mark the playing Video with a very light blue background and a thin indicator. Preserve import, removal, clear, selection, language-pair selection, error feedback, and Auto-advance.
- **Player:** Use a plain black stage with minimal framing. Keep the current empty-state open-video action and drag-and-drop behavior, with simpler presentation.
- **Transport:** A flat strip always visible below the Video in windowed mode. Place the timeline above the controls, make play/pause the clearest control near the center, and keep volume and fullscreen on the right. In fullscreen, overlay the strip on the Video and retain its current auto-hide behavior. Preserve previous/next, seek, speed, volume, and keyboard controls.
- **Dialogs:** Apply the same light, compact, flat visual language to Settings and Subtitle Generation. Keep their existing fields, states, and actions. They follow the active theme.

## Themes and visual rules

- Light is the default for a user with no saved theme; a saved preference still wins.
- Dark uses neutral dark grays and the same muted blue accent, density, geometry, and visual hierarchy as light.
- Use system-style typography, clear labels, thin borders, modest spacing, and small corner radii. Keep the play button round.
- Maintain visible hover, focus, disabled, error, and processing states without adding decorative effects.
- Preserve sufficient text and control contrast in both themes.

## Scope

This is a visual and layout redesign. It does not change the domain model or the behavior of Video playback, Playback Queue, Subtitle Jobs, subtitle display preferences, or Subtitle Export.
