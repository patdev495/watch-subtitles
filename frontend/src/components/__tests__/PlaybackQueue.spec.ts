import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import PlaybackQueue from '../PlaybackQueue.vue';

const videos = [
  { path: '/videos/a.mp4', filename: 'a.mp4', sourceLanguage: 'en', cachedPairs: [['en', 'vi']] as [string, string][] },
  { path: '/videos/b.mp4', filename: 'b.mp4', sourceLanguage: 'ja', cachedPairs: [] as [string, string][] },
];

describe('PlaybackQueue', () => {
  it('offers a clear-all action only when Playback Queue has videos', async () => {
    const wrapper = mount(PlaybackQueue, { props: { videos, jobs: [], activePath: '', autoAdvance: true } });
    await wrapper.get('button[aria-label="Xóa tất cả video khỏi hàng đợi phát"]').trigger('click');
    expect(wrapper.emitted('clear')).toHaveLength(1);
    await wrapper.setProps({ videos: [] });
    expect(wrapper.get('button[aria-label="Xóa tất cả video khỏi hàng đợi phát"]').attributes('disabled')).toBeDefined();
  });
  it('shows active video, availability, job progress, and emits separate select/remove actions', async () => {
    const wrapper = mount(PlaybackQueue, {
      props: {
        videos, activePath: '/videos/a.mp4', autoAdvance: true,
        jobs: [{ id: 'job', video_path: '/videos/b.mp4', source_language: 'ja', target_language: 'vi', status: 'processing', progress: 62, step: '', cues: [], error: null, cached: false }],
      },
    });

    expect(wrapper.get('[data-test="queue-row-active"]').text()).toContain('a.mp4');
    expect(wrapper.text()).toContain('en → vi');
    expect(wrapper.text()).toContain('62%');
    await wrapper.get('[data-test="queue-select-b"]').trigger('click');
    await wrapper.get('[data-test="queue-remove-b"]').trigger('click');
    expect(wrapper.emitted('select')?.[0]).toEqual([videos[1]]);
    expect(wrapper.emitted('remove')?.[0]).toEqual([videos[1]]);
  });
});
