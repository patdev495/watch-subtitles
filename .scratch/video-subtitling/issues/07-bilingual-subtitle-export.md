Status: done

# Issue 07: Bilingual Subtitle Export (.SRT / .VTT)

## Parent
.scratch/video-subtitling/PRD.md

## What to build
Allow users to export the synchronized bilingual subtitles into standard standalone subtitle files (`.srt` and `.vtt`) so they can be saved to disk and loaded into external players like VLC or uploaded to video platforms.

When the user clicks the "Export Subtitles" button, they can choose the desired format (`.srt` or `.vtt`) and subtitle layout (e.g. Bilingual with original on top and translated below, or separate original/translated tracks). The Python backend generates the formatted string, invokes a native "Save As" file dialog, and writes the file.

## Acceptance criteria
- [ ] Export button placed in the player/footer header bar, enabled only when active cues exist.
- [ ] Formatter utility generates valid SRT syntax with sequence numbers, `00:00:00,000 --> 00:00:00,000` timestamps, and dual-language text blocks.
- [ ] Formatter utility generates valid WebVTT syntax (`WEBVTT` header, `00:00:00.000 --> 00:00:00.000` timestamps).
- [ ] Native file save dialog allows the user to choose target destination on disk.
- [ ] Exported files load correctly and display dual subtitles in VLC / media players.

## Blocked by
.scratch/video-subtitling/issues/06-stt-translation-pipeline.md
