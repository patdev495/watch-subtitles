Status: done

# Issue 02: Local Video Loading & Playback

## Parent
.scratch/video-subtitling/PRD.md

## What to build
Implement local video file selection and playback inside the desktop app. Users can select a video file either through a native file dialog (provided via the Python backend bridge) or by dragging and dropping a media file into the app window.

The selected video is loaded into a custom-styled HTML5 `<video>` player component with standard playback controls: Play/Pause, Seek bar, Current Time / Duration display, Volume / Mute, and Playback Speed selector.

## Acceptance criteria
- [x] User can click an "Open Video" button which calls the Python backend to open a native OS file dialog filtering for common video formats (`.mp4`, `.mkv`, `.webm`, `.avi`, `.mov`).
- [x] User can drag-and-drop a video file onto the application window to load it.
- [x] Video streams or loads smoothly in the Vue player without CORS or local file path restriction issues in `pywebview`.
- [x] Custom video player controls function accurately (Play/Pause toggling, accurate seeking, volume adjustment).
- [x] Video state (current time in seconds, duration, isPlaying) is reactively tracked and emitted to parent components.

## Blocked by
.scratch/video-subtitling/issues/01-project-skeleton-desktop-shell.md
