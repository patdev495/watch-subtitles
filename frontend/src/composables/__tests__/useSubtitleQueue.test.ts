import { describe, expect, it } from 'vitest';
import { ref } from 'vue';
import { useSubtitleQueue } from '../useSubtitleQueue';
import type { SubtitleJob } from '../../types';

const processingJob = (progress: number): SubtitleJob => ({
  id: 'main-job', video_path: '/videos/lesson.mp4', source_language: 'en', target_language: 'vi',
  status: 'processing', progress, step: `Đang xử lý ${progress}%`, cues: [], error: null, cached: false,
});

describe('useSubtitleQueue', () => {
  it('notifies the main player for every progress update, including the same job status', () => {
    const updates: SubtitleJob[] = [];
    const { updateSubtitleJob } = useSubtitleQueue(ref('/videos/lesson.mp4'), (job) => updates.push(job), ref(false));

    updateSubtitleJob(processingJob(12));
    updateSubtitleJob(processingJob(64));

    expect(updates.map((job) => job.progress)).toEqual([12, 64]);
  });
});
