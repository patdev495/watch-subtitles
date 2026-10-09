# Language-aware Subtitle Cache

Subtitle Cache entries are keyed by Video Fingerprint, Source Language, and Target Language. A Video can be transcribed differently for each selected Source Language, so retaining the existing fingerprint-plus-target key could return Cues from an incompatible transcription; existing cache data does not need migration.
