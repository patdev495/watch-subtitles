import { computed, type Ref } from 'vue';
import type { Cue } from '../types';

export interface UseTranscriptReturn {
  activeCue: Readonly<Ref<Cue | null>>;
  activeCueIndex: Readonly<Ref<number>>;
}

/**
 * Tracks the currently active subtitle cue based on video playback time.
 *
 * @param cues    - Reactive list of all Cue items (ordered by start time)
 * @param currentTime - Reactive current playback position in seconds
 */
export function useTranscript(
  cues: Ref<Cue[]>,
  currentTime: Ref<number>,
): UseTranscriptReturn {
  const activeCueIndex = computed<number>(() => {
    const t = currentTime.value;
    return cues.value.findIndex((c) => t >= c.start && t < c.end);
  });

  const activeCue = computed<Cue | null>(() => {
    const idx = activeCueIndex.value;
    return idx >= 0 ? cues.value[idx] : null;
  });

  return { activeCue, activeCueIndex };
}
