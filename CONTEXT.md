# Video Subtitling & Playback

Desktop application domain for local video playback with automated external speech-to-text transcription and bilingual subtitle display.

## Language

**Video**:
A local media file containing visual content and embedded audio.
_Avoid_: Movie, stream, clip

**Audio Track**:
The extracted audio stream isolated from the video for external processing.
_Avoid_: Sound file, voice record

**Original Subtitle**:
Timestamped text cues transcribed directly from the video's spoken dialogue.
_Avoid_: Source caption, closed caption

**Translated Subtitle**:
Timestamped text cues converted from the original subtitles into the user's chosen target language.
_Avoid_: Target transcript, subtitle dub

**Transcription (STT)**:
The process of sending extracted audio to an external API to generate timestamped text cues.
_Avoid_: Speech synthesis, TTS, voice typing

**Translation**:
The process of converting textual subtitle cues into another language while preserving their timecodes.
_Avoid_: Transliteration, dubbing

**Cue**:
A distinct unit of subtitle speech bounded by precise start and end timestamps.
_Avoid_: Line, block, segment

**Interactive Transcript Footer**:
A playback footer that displays the synchronized Bilingual Display for the current active Cue.
_Avoid_: Subtitle tray, transcript bar, cue list

**Bilingual Display**:
The visual presentation of both the original and translated subtitle text within the current active cue.
_Avoid_: Split caption, dual overlay

**Pinyin Line**:
Tone-marked Romanized Mandarin pronunciation displayed directly beneath a subtitle line containing Chinese characters.
_Avoid_: Chinese translation, phonetic cue

**Transcription Provider**:
An external speech-to-text cloud service configured by the user (e.g. Deepgram).
_Avoid_: Engine, local model

**Translation Provider**:
An external text translation cloud service configured by the user (e.g. DeepL).
_Avoid_: Machine translator, dictionary

**Video Fingerprint**:
A deterministic content hash identifying a Video file regardless of its filename or filesystem location.
_Avoid_: File path, video ID, checksum

**Subtitle Cache**:
The local persistent store that preserves generated Cues keyed by Video Fingerprint to prevent duplicate API expenses.
_Avoid_: Local storage, database, project file

**Target Language**:
The chosen language into which the original subtitles are translated.
_Avoid_: Destination language, output dialect

**Source Language**:
The language selected by the user for the spoken dialogue in a Video.
_Avoid_: Input language, detected language

**Subtitle Export**:
The process of serializing the synchronized bilingual cues into a standalone media file (`.srt` or `.vtt`).
_Avoid_: Save as, dump, render

**API Credential**:
A secret authentication token supplied by the user to authorize requests to external providers.
_Avoid_: Password, license key

## Relationships

- A **Video** yields exactly one **Video Fingerprint** derived from its content
- The **Subtitle Cache** checks for existing **Cue** items matching the **Video Fingerprint** before making any external calls
- If not cached, the **Video** yields an **Audio Track** that is dispatched to a **Transcription Provider** using an **API Credential** to produce a sequence of **Cue** items with **Original Subtitle** text
- Each **Cue** has its **Original Subtitle** dispatched from the chosen **Source Language** to a **Translation Provider** to generate a matching **Translated Subtitle** in the chosen **Target Language**
- Completed **Cue** items are stored into the **Subtitle Cache** under the **Video Fingerprint**
- The **Interactive Transcript Footer** renders one current active **Cue** as its **Bilingual Display** during video playback or seeking
- The user can trigger a **Subtitle Export** to save the synchronized bilingual cues to an `.srt` or `.vtt` file on disk

## Example dialogue

> **Dev:** "Do we feed the raw **Video** file to the external API?"
> **Domain expert:** "No — we extract the **Audio Track** locally first, then send only that track for **Transcription (STT)**."
> **Dev:** "How does the user navigate using subtitles?"
> **Domain expert:** "The **Interactive Transcript Footer** highlights the active **Cue** with its **Bilingual Display**, and clicking any cue immediately seeks the **Video** to that moment."

## Flagged ambiguities

- "TTS" was previously used to describe subtitle extraction — resolved: the system performs **Transcription (STT)** (Speech-to-Text), not TTS (Text-to-Speech).
