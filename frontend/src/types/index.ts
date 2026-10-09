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
}

declare global {
  interface Window {
    pywebview?: {
      api: PyWebViewApi;
    };
  }
}
