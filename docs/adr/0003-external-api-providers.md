# External Providers: Deepgram for STT and DeepL for Translation

We decided to use Deepgram as the primary external Speech-to-Text provider and DeepL as the primary external Translation provider, configured via Bring-Your-Own-Key (BYOK).

Deepgram provides ultra-fast transcription with precise word and sentence timestamps at low cost. DeepL provides high-quality sentence-level translations with a free tier API. Both integrations are wrapped behind abstract provider interfaces so alternative engines (e.g. Gemini, OpenAI Whisper) can be plugged in without changing domain logic.
