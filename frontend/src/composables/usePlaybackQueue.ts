import { computed, onScopeDispose, ref, watch, type Ref } from 'vue';
import type { PlaybackQueueState, PlaybackVideo } from '../types';

interface PlaybackQueueCallbacks {
  openVideo: (path: string, source?: string, target?: string, resumeAt?: number) => Promise<void>;
  stopPlayback: () => void;
  duplicateImport: (path: string) => void;
}

export function usePlaybackQueue(
  currentTime: Ref<number>,
  sourceLanguage: Ref<string>,
  callbacks: PlaybackQueueCallbacks,
) {
  const queuedVideos = ref<PlaybackVideo[]>([]);
  const currentFilePath = ref('');
  const autoAdvance = ref(true);
  const restoreTime = ref(0);
  const restored = ref(false);
  const queueIndex = computed(() => queuedVideos.value.findIndex((video) => video.path === currentFilePath.value));
  const hasPrevious = computed(() => queueIndex.value > 0);
  const hasNext = computed(() => queueIndex.value >= 0 && queueIndex.value < queuedVideos.value.length - 1);
  let restorePending: Promise<void> | undefined;
  let persistTimer: ReturnType<typeof setTimeout> | undefined;
  let persistPending: Promise<void> = Promise.resolve();

  function saveQueue(): void {
    const api = window.pywebview?.api;
    if (!restored.value || !api?.save_playback_queue) return;
    const snapshot: PlaybackQueueState = {
      videos: queuedVideos.value.map((video) => ({
        path: video.path,
        source_language: video.sourceLanguage ?? 'en',
        target_language: video.targetLanguage ?? null,
      })),
      selected_path: currentFilePath.value,
      playback_time: currentTime.value,
      auto_advance: autoAdvance.value,
    };
    persistPending = persistPending
      .then(async () => { await api.save_playback_queue(snapshot); })
      .catch((error: unknown) => { console.error('Failed to save Playback Queue:', error); });
  }

  watch([queuedVideos, currentFilePath, autoAdvance], saveQueue, { deep: true });
  watch(currentTime, () => {
    if (!restored.value || !window.pywebview?.api?.save_playback_queue) return;
    if (persistTimer) clearTimeout(persistTimer);
    persistTimer = setTimeout(saveQueue, 250);
  });
  onScopeDispose(() => { if (persistTimer) clearTimeout(persistTimer); });

  function restoreQueue(): Promise<void> {
    if (restorePending) return restorePending;
    const api = window.pywebview?.api;
    if (!api) return Promise.resolve();
    if (!api.get_playback_queue) {
      restored.value = true;
      return Promise.resolve();
    }
    restorePending = (async () => {
      try {
        const state = await api.get_playback_queue();
        autoAdvance.value = state.auto_advance;
        for (const video of state.videos) {
          const cached = await api.get_cached_subtitle_languages(video.path);
          queuedVideos.value.push({
            path: video.path,
            filename: video.path.split(/[/\\]/).pop() ?? video.path,
            sourceLanguage: video.source_language,
            targetLanguage: video.target_language ?? undefined,
            cachedPairs: cached.ok ? cached.language_pairs : [],
          });
        }
        if (state.selected_path) {
          const selected = queuedVideos.value.find((video) => video.path === state.selected_path);
          await callbacks.openVideo(
            state.selected_path,
            selected?.sourceLanguage,
            selected?.targetLanguage,
            state.playback_time,
          );
        }
      } catch (error) {
        console.error('Failed to restore Playback Queue:', error);
      } finally {
        restored.value = true;
      }
    })();
    return restorePending;
  }

  async function rememberOpenedVideo(
    path: string,
    filename: string,
    source?: string,
    target?: string,
    isCurrent: () => boolean = () => true,
  ): Promise<PlaybackVideo | undefined> {
    const existing = queuedVideos.value.find((video) => video.path === path);
    if (existing) {
      existing.error = undefined;
      return existing;
    }
    const cached = await window.pywebview?.api?.get_cached_subtitle_languages?.(path);
    if (!isCurrent()) return undefined;
    const video: PlaybackVideo = {
      path,
      filename,
      sourceLanguage: source ?? sourceLanguage.value,
      targetLanguage: target,
      cachedPairs: cached?.ok ? cached.language_pairs : [],
    };
    queuedVideos.value.push(video);
    return video;
  }

  async function importQueue(kind: 'files' | 'folder'): Promise<void> {
    const api = window.pywebview?.api;
    if (!api) return;
    const result = kind === 'files'
      ? (api.open_video_files_dialog
        ? await api.open_video_files_dialog()
        : { cancelled: false, videos: [await api.open_video_dialog()] })
      : await api.open_video_folder_dialog();
    if (result.cancelled) return;
    for (const entry of result.videos) {
      if (!entry.path || !entry.filename) continue;
      if (queuedVideos.value.some((video) => video.path === entry.path)) {
        callbacks.duplicateImport(entry.path);
        continue;
      }
      const cached = await api.get_cached_subtitle_languages(entry.path);
      queuedVideos.value.push({
        path: entry.path,
        filename: entry.filename,
        sourceLanguage: sourceLanguage.value,
        cachedPairs: cached.ok ? cached.language_pairs : [],
      });
    }
  }

  async function selectQueueVideo(video: PlaybackVideo): Promise<void> {
    await callbacks.openVideo(video.path, video.sourceLanguage, video.targetLanguage);
  }

  function setOpenedVideo(path: string, resumeAt = 0): void {
    currentFilePath.value = path;
    restoreTime.value = resumeAt;
    currentTime.value = resumeAt;
  }

  function setVideoLanguages(video: PlaybackVideo, source: string, target?: string): void {
    video.sourceLanguage = source;
    if (target !== undefined) video.targetLanguage = target;
  }

  function recordSubtitleAvailability(path: string, source: string, target: string): void {
    const video = queuedVideos.value.find((item) => item.path === path);
    if (video && !video.cachedPairs?.some(([cachedSource, cachedTarget]) => cachedSource === source && cachedTarget === target)) {
      video.cachedPairs = [...(video.cachedPairs ?? []), [source, target]];
    }
  }

  function markPlaybackError(path: string): void {
    const video = queuedVideos.value.find((item) => item.path === path);
    if (video) video.error = 'Không thể phát video.';
  }

  async function removePlaybackVideo(video: PlaybackVideo): Promise<void> {
    const index = queuedVideos.value.findIndex((item) => item.path === video.path);
    if (index < 0) return;
    const wasActive = currentFilePath.value === video.path;
    queuedVideos.value.splice(index, 1);
    if (wasActive) {
      stopPlayback();
      const next = queuedVideos.value[index] ?? queuedVideos.value[0];
      if (next) await selectQueueVideo(next);
    }
  }

  function stopPlayback(): void {
    currentFilePath.value = '';
    currentTime.value = 0;
    restoreTime.value = 0;
    callbacks.stopPlayback();
  }

  function clearPlaybackQueue(): void {
    if (queuedVideos.value.length === 0) return;
    queuedVideos.value = [];
    stopPlayback();
  }

  async function playNext(): Promise<void> {
    if (queueIndex.value < 0) return;
    for (const video of queuedVideos.value.slice(queueIndex.value + 1)) {
      await selectQueueVideo(video);
      if (currentFilePath.value === video.path && !video.error) return;
    }
  }

  async function playPrevious(): Promise<void> {
    if (queueIndex.value <= 0) return;
    for (const video of queuedVideos.value.slice(0, queueIndex.value).reverse()) {
      await selectQueueVideo(video);
      if (currentFilePath.value === video.path && !video.error) return;
    }
  }

  async function advanceQueue(): Promise<void> {
    if (autoAdvance.value) await playNext();
  }

  function handlePlaybackError(): void {
    markPlaybackError(currentFilePath.value);
    void advanceQueue();
  }

  return {
    queuedVideos, currentFilePath, autoAdvance, restoreTime, hasPrevious, hasNext,
    restoreQueue, rememberOpenedVideo, importQueue, selectQueueVideo, setOpenedVideo, setVideoLanguages,
    recordSubtitleAvailability, markPlaybackError, removePlaybackVideo, clearPlaybackQueue,
    playNext, playPrevious, advanceQueue, handlePlaybackError,
  };
}
