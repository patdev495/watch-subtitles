import { reactive } from 'vue';

interface ThumbnailState {
  urls: Record<string, string>;
  failed: Record<string, boolean>;
}

const state = reactive<ThumbnailState>({ urls: {}, failed: {} });
const pending = new Set<string>();

/**
 * Resolves per-Video poster thumbnails through the backend, which caches one
 * JPEG per Video Fingerprint. Without the bridge (browser dev) or when a frame
 * cannot be extracted, callers fall back to a generated placeholder tile.
 */
export function useThumbnails() {
  async function loadThumbnail(videoPath: string): Promise<void> {
    if (!videoPath || state.urls[videoPath] || state.failed[videoPath] || pending.has(videoPath)) return;
    const api = window.pywebview?.api;
    if (!api?.get_thumbnail_url) return;
    pending.add(videoPath);
    try {
      const res = await api.get_thumbnail_url(videoPath);
      if (res.ok && res.url) state.urls[videoPath] = res.url;
      else state.failed[videoPath] = true;
    } catch (error) {
      console.error('Failed to resolve video thumbnail:', error);
      state.failed[videoPath] = true;
    } finally {
      pending.delete(videoPath);
    }
  }

  function failThumbnail(videoPath: string): void {
    delete state.urls[videoPath];
    state.failed[videoPath] = true;
  }

  function thumbnailUrl(videoPath: string): string | undefined {
    return state.failed[videoPath] ? undefined : state.urls[videoPath];
  }

  return { loadThumbnail, failThumbnail, thumbnailUrl };
}
