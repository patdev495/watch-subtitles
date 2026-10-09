export interface Cue {
  id: string;
  start: number; // in seconds
  end: number;   // in seconds
  originalText: string;
  translatedText: string;
}

export interface VideoDialogResponse {
  cancelled: boolean;
  path?: string;
  filename?: string;
  stream_url?: string;
}

export interface PingResponse {
  status: string;
  message: string;
}

export interface AppSettings {
  deepgram_api_key: string;
  deepl_api_key: string;
  default_target_language: string;
  stt_provider: string;
  translation_provider: string;
  tts_provider?: string;
  tts_api_key?: string;
}

export interface TestConnectionResponse {
  ok: boolean;
  message: string;
}

export interface CachedSubtitlesResponse {
  ok: boolean;
  cached: boolean;
  fingerprint?: string;
  cues: Cue[];
  error?: string;
}

export interface AudioExtractionResponse {
  ok: boolean;
  audio_path?: string;
  error?: string;
}

export interface PyWebViewApi {
  ping: () => Promise<PingResponse>;
  open_video_dialog: () => Promise<VideoDialogResponse>;
  load_video_path: (path: string) => Promise<VideoDialogResponse>;
  get_settings: () => Promise<AppSettings>;
  save_settings: (data: AppSettings) => Promise<AppSettings>;
  test_connection: (
    provider_type: 'stt' | 'translation' | 'tts',
    provider_name: string,
    api_key: string,
  ) => Promise<TestConnectionResponse>;
  get_video_fingerprint: (video_path: string) => Promise<{ ok: boolean; fingerprint?: string; error?: string }>;
  get_cached_subtitles: (video_path: string, target_language: string) => Promise<CachedSubtitlesResponse>;
  save_cached_subtitles: (video_path: string, target_language: string, cues: Cue[]) => Promise<{ ok: boolean; fingerprint?: string; error?: string }>;
  extract_video_audio: (video_path: string) => Promise<AudioExtractionResponse>;
}

declare global {
  interface Window {
    pywebview?: {
      api: PyWebViewApi;
    };
  }
}
