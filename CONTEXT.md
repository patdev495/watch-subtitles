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

**Subtitle Job**:
A request to generate Original and Translated Subtitles for one Video and one selected Source Language–Target Language pair. Jobs not completed when the application closes stop, while completed Subtitle Cache data remains available.
_Avoid_: Translation task, pipeline run, background task

**Playback Queue**:
The ordered list of Videos available to play across application launches. It is also the sole collection from which Subtitle Jobs may be requested; adding a Video does not create a Subtitle Job, and selecting a Video for playback does not remove it from the Playback Queue. Selecting a Video loads and plays it. Removing the Video currently playing stops playback and selects the next queued Video, or leaves the player empty when none remains, but never cancels that Video's Subtitle Jobs. On restoration, missing Video paths are omitted, and the last selected Video resumes at its saved playback time. A Video that cannot play remains in the queue with an error, but Auto-advance skips it.
_Avoid_: Subtitle Queue, playlist, pending job

**Queue Import**:
The addition of one or more unique Videos to the end of the Playback Queue by choosing video files or a folder in the operating-system dialog. Multi-file selection preserves the user's chosen order. A folder import includes only supported video files directly inside that folder, not its subfolders, sorted by filename from A to Z. An attempted duplicate is not added and reports “Video đã trong hàng đợi rồi.”
_Avoid_: Upload, scan

**Auto-advance**:
An optional playback setting, enabled by default on first use and then restored from the user's saved preference, that loads and plays the next Video in the Playback Queue when the current Video ends.
_Avoid_: Autoplay, continuous play

**Subtitle Availability**:
The set of Source Language–Target Language pairs for which a Video has cached subtitles. It is presented on that Video in the Playback Queue as one or more language pairs.
_Avoid_: Has subtitles, subtitle status

**Active Subtitles**:
The most recently created cached subtitle pair for the Video currently playing. If no pair exists, playback has no subtitles.
_Avoid_: Selected subtitles, current language pair

**Subtitle Display Preferences**:
The user's saved, application-wide choices for showing subtitle lines and their font sizes in the player. The video overlay shows one primary line (Original Subtitle or Translated Subtitle), while the player display panel shows both. These preferences are restored across application launches and are separate from Subtitle Job creation.
_Avoid_: Subtitle generation settings, caption style

**Subtitle Generation Modal**:
The dialog that lists Playback Queue Videos for initiating Subtitle Jobs. It may close while jobs run in the background and reopens with their progress. The matching Video row in the Playback Queue also shows that progress. It supports creating a job for one selected Video or for all eligible Videos, with a separately editable Source Language–Target Language pair for each Video. “Create all” creates jobs only for Videos without Subtitle Availability for their selected pair, in Playback Queue order. Rows with waiting or processing jobs for their selected pair cannot create duplicates; failed jobs can be retried.
_Avoid_: Subtitle Queue, generation screen

**Target Language**:
The chosen language into which the original subtitles are translated.
_Avoid_: Destination language, output dialect

**Source Language**:
The language selected by the user for the spoken dialogue in a Video. A Video in the Playback Queue retains its own Source Language and it is configured in the Subtitle Generation Modal.
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
- A **Video** in the **Playback Queue** becomes a **Subtitle Job** when the user requests generation for it in the **Subtitle Generation Modal**, individually or for all eligible Videos
- A **Subtitle Job** retains the Source Language and Target Language selected when generation was requested
- **Subtitle Jobs** are processed one at a time in first-in, first-out order without changing the Video currently selected for playback
- A failed **Subtitle Job** is reported to the user and does not prevent the next **Subtitle Job** from being processed
- The user can retry a failed **Subtitle Job**, which enters the end of the processing order with its original language pair
- A **Video** remains in the **Playback Queue** after its Subtitle Job completes or fails, until the user removes it; removing it does not cancel any of its Subtitle Jobs
- The **Interactive Transcript Footer** renders one current active **Cue** as its **Bilingual Display** during video playback or seeking
- The user can trigger a **Subtitle Export** to save the synchronized bilingual cues to an `.srt` or `.vtt` file on disk

## Example dialogue

> **Dev:** "Do we feed the raw **Video** file to the external API?"
> **Domain expert:** "No — we extract the **Audio Track** locally first, then send only that track for **Transcription (STT)**."
> **Dev:** "How does the user navigate using subtitles?"
> **Domain expert:** "The **Interactive Transcript Footer** highlights the active **Cue** with its **Bilingual Display**, and clicking any cue immediately seeks the **Video** to that moment."

## Flagged ambiguities

- "TTS" was previously used to describe subtitle extraction — resolved: the system performs **Transcription (STT)** (Speech-to-Text), not TTS (Text-to-Speech).
