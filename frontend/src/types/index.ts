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

export interface PyWebViewApi {
  ping: () => Promise<PingResponse>;
  open_video_dialog: () => Promise<VideoDialogResponse>;
  load_video_path: (path: string) => Promise<VideoDialogResponse>;
}

declare global {
  interface Window {
    pywebview?: {
      api: PyWebViewApi;
    };
  }
}
