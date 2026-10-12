import { watch, type Ref } from 'vue';
import type { PlaybackQueueState, PlaybackVideo } from '../types';

export function usePlaybackQueuePersistence(
  queuedVideos: Ref<PlaybackVideo[]>,
  currentFilePath: Ref<string>,
  currentTime: Ref<number>,
  autoAdvance: Ref<boolean>,
  restored: Ref<boolean>,
): void {
  let persistTimer: ReturnType<typeof setTimeout> | undefined;
  let persistPending: Promise<void> = Promise.resolve();

  function saveQueue(): void {
    const api = window.pywebview?.api;
    if (!restored.value || !api?.save_playback_queue) return;
    const snapshot: PlaybackQueueState = {
      videos: queuedVideos.value.map((video) => ({ path: video.path, source_language: video.sourceLanguage ?? 'en', target_language: video.targetLanguage ?? null })),
      selected_path: currentFilePath.value,
      playback_time: currentTime.value,
      auto_advance: autoAdvance.value,
    };
    persistPending = persistPending.then(async () => { await api.save_playback_queue(snapshot); }).catch((error: unknown) => { console.error('Failed to save Playback Queue:', error); });
  }

  watch([queuedVideos, currentFilePath, autoAdvance], saveQueue, { deep: true });
  watch(currentTime, () => {
    if (!restored.value || !window.pywebview?.api?.save_playback_queue) return;
    if (persistTimer) clearTimeout(persistTimer);
    persistTimer = setTimeout(saveQueue, 250);
  });
}
