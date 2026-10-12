import { computed, type Ref } from 'vue';
import type { PlaybackVideo } from '../types';

/**
 * Moving through the Playback Queue. Both directions skip Videos that cannot
 * play, and stop at the ends of the queue instead of wrapping.
 */
export function useQueueNavigation(
  queuedVideos: Ref<PlaybackVideo[]>,
  currentFilePath: Ref<string>,
  selectVideo: (video: PlaybackVideo) => Promise<void>,
) {
  const queueIndex = computed(() => queuedVideos.value.findIndex((video) => video.path === currentFilePath.value));
  const hasPrevious = computed(() => queueIndex.value > 0);
  const hasNext = computed(() => queueIndex.value >= 0 && queueIndex.value < queuedVideos.value.length - 1);

  async function playNext(): Promise<void> {
    if (queueIndex.value < 0) return;
    for (const video of queuedVideos.value.slice(queueIndex.value + 1)) {
      await selectVideo(video);
      if (currentFilePath.value === video.path && !video.error) return;
    }
  }

  async function playPrevious(): Promise<void> {
    if (queueIndex.value <= 0) return;
    for (const video of queuedVideos.value.slice(0, queueIndex.value).reverse()) {
      await selectVideo(video);
      if (currentFilePath.value === video.path && !video.error) return;
    }
  }

  return { queueIndex, hasPrevious, hasNext, playNext, playPrevious };
}
