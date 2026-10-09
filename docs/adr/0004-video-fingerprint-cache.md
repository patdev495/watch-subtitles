# Video Fingerprint Caching

We decided to key local subtitle caching by a deterministic content hash (`Video Fingerprint`) rather than the filesystem path.

Video files are often renamed, organized into new directories, or moved across drives. Keying cached transcription and translation cues by content fingerprint guarantees that moving a file does not trigger redundant, costly calls to external APIs. For performance on large media files, the fingerprint is computed using a fast chunked hash (e.g. file size + head/tail sampling).
