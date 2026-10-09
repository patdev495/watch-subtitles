# Desktop Architecture for Video Subtitling

We decided to build `watch-subtitles` as a desktop application rather than a web application.

Video processing and audio extraction run locally on the user's machine using FFmpeg. Only lightweight compressed audio and text payloads are sent to external cloud APIs for transcription and translation. This eliminates heavy server-side video bandwidth, expensive cloud storage, and privacy concerns, while giving the user full local control over their media files and API keys.
