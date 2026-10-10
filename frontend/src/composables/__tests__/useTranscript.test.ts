import { describe, it, expect } from 'vitest';
import { ref } from 'vue';
import { useTranscript } from '../useTranscript';
import type { Cue } from '../../types';

const makeCue = (id: string, start: number, end: number): Cue => ({
  id,
  start,
  end,
  originalText: `Original ${id}`,
  translatedText: `Translated ${id}`,
});

const SAMPLE_CUES: Cue[] = [
  makeCue('1', 0, 3),
  makeCue('2', 3, 7),
  makeCue('3', 7, 12),
];

describe('useTranscript', () => {
  // ── Slice 1: empty cues ──────────────────────────────────────────────────────
  it('returns null activeCue when cues list is empty', () => {
    const { activeCue } = useTranscript(ref([]), ref(0));
    expect(activeCue.value).toBeNull();
  });

  // ── Slice 2: time within first cue ──────────────────────────────────────────
  it('returns first cue when currentTime is within its range', () => {
    const { activeCue } = useTranscript(ref(SAMPLE_CUES), ref(1.5));
    expect(activeCue.value?.id).toBe('1');
  });

  // ── Slice 3: time within second cue ─────────────────────────────────────────
  it('returns second cue when currentTime is within its range', () => {
    const { activeCue } = useTranscript(ref(SAMPLE_CUES), ref(5));
    expect(activeCue.value?.id).toBe('2');
  });

  // ── Slice 4: time between cues (gap) ────────────────────────────────────────
  it('returns null when currentTime falls between cues', () => {
    const cuesWithGap: Cue[] = [makeCue('a', 0, 2), makeCue('b', 5, 8)];
    const { activeCue } = useTranscript(ref(cuesWithGap), ref(3.5));
    expect(activeCue.value).toBeNull();
  });

  // ── Slice 5: time at exact boundary (start) ──────────────────────────────────
  it('activates cue when currentTime equals cue start', () => {
    const { activeCue } = useTranscript(ref(SAMPLE_CUES), ref(3));
    expect(activeCue.value?.id).toBe('2');
  });

  it('shows an upcoming cue shortly before its first timed word', () => {
    const { activeCue } = useTranscript(ref([makeCue('spoken', 10, 12)]), ref(9.75));
    expect(activeCue.value?.id).toBe('spoken');
  });

  // ── Slice 6: time past all cues ──────────────────────────────────────────────
  it('returns null when currentTime is after all cues', () => {
    const { activeCue } = useTranscript(ref(SAMPLE_CUES), ref(999));
    expect(activeCue.value).toBeNull();
  });

  // ── Slice 7: activeCueIndex matches activeCue position ───────────────────────
  it('activeCueIndex matches index of activeCue in cues array', () => {
    const { activeCueIndex } = useTranscript(ref(SAMPLE_CUES), ref(9));
    expect(activeCueIndex.value).toBe(2); // third cue (id='3')
  });

  // ── Slice 8: reacts to currentTime change ────────────────────────────────────
  it('updates activeCue reactively when currentTime changes', () => {
    const currentTime = ref(1);
    const { activeCue } = useTranscript(ref(SAMPLE_CUES), currentTime);
    expect(activeCue.value?.id).toBe('1');
    currentTime.value = 5;
    expect(activeCue.value?.id).toBe('2');
  });

  // ── Slice 9: 50+ cues (scale check) ──────────────────────────────────────────
  it('handles 50+ cues and finds correct active cue', () => {
    const bigCues: Cue[] = Array.from({ length: 60 }, (_, i) =>
      makeCue(String(i), i * 5, i * 5 + 4.9),
    );
    const { activeCue } = useTranscript(ref(bigCues), ref(147.3)); // within cue 29
    expect(activeCue.value?.id).toBe('29');
  });
});
