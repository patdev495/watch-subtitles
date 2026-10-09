import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import QueueScreen from '../QueueScreen.vue';

describe('QueueScreen', () => {
  it('starts a job for one queued video with the current language pair', async () => {
    const wrapper = mount(QueueScreen, {
      props: {
        videos: [{ path: '/videos/lesson.mp4', filename: 'lesson.mp4' }],
        jobs: [],
        sourceLanguage: 'en',
        targetLanguage: 'vi',
      },
    });

    expect(wrapper.text()).toContain('#1');
    expect((wrapper.get('[data-test="source-language"]').element as HTMLSelectElement).value).toBe('en');
    expect((wrapper.get('[data-test="target-language"]').element as HTMLSelectElement).value).toBe('vi');
    await wrapper.get('[data-test="play-video"]').trigger('click');
    expect(wrapper.emitted('play')).toEqual([[{ path: '/videos/lesson.mp4', filename: 'lesson.mp4' }]]);
    await wrapper.get('[data-test="generate-video"]').trigger('click');

    expect(wrapper.emitted('generate')).toEqual([[{ path: '/videos/lesson.mp4', filename: 'lesson.mp4' }, 'en', 'vi']]);
  });

  it('keeps a failed video visible and exposes retry with original language pair', async () => {
    const wrapper = mount(QueueScreen, {
      props: {
        videos: [{ path: '/videos/lesson.mp4', filename: 'lesson.mp4' }],
        jobs: [{
          id: 'failed-job', video_path: '/videos/lesson.mp4', source_language: 'ja', target_language: 'vi',
          status: 'failed', progress: 0, step: 'Lỗi', cues: [], error: 'offline', cached: false,
        }],
        sourceLanguage: 'en',
        targetLanguage: 'vi',
      },
    });

    expect(wrapper.text()).toContain('lesson.mp4');
    await wrapper.get('[data-test="retry-job"]').trigger('click');
    expect(wrapper.emitted('retry')).toEqual([['failed-job']]);
  });

  it('allows removal only for a waiting job', async () => {
    const wrapper = mount(QueueScreen, {
      props: {
        videos: [{ path: '/videos/lesson.mp4', filename: 'lesson.mp4' }],
        jobs: [{ id: 'waiting-job', video_path: '/videos/lesson.mp4', source_language: 'en', target_language: 'vi', status: 'waiting', progress: 0, step: 'wait', cues: [], error: null, cached: false }],
        sourceLanguage: 'en', targetLanguage: 'vi',
      },
    });

    await wrapper.get('[data-test="remove-job"]').trigger('click');
    expect(wrapper.emitted('remove-job')).toEqual([['waiting-job']]);
  });

  it('uses each video selected language pair and flags a matching cache as recreation', async () => {
    const wrapper = mount(QueueScreen, {
      props: {
        videos: [{ path: '/videos/lesson.mp4', filename: 'lesson.mp4', cachedPairs: [['zh-CN', 'vi']] }], jobs: [], sourceLanguage: 'en', targetLanguage: 'vi',
      },
    });

    await wrapper.get('[data-test="source-language"]').setValue('zh-CN');
    expect(wrapper.get('[data-test="generate-video"]').text()).toContain('Tạo lại phụ đề');
    await wrapper.get('[data-test="generate-video"]').trigger('click');
    expect(wrapper.emitted('generate')).toEqual([[{ path: '/videos/lesson.mp4', filename: 'lesson.mp4', cachedPairs: [['zh-CN', 'vi']] }, 'zh-CN', 'vi']]);
    await wrapper.get('.queue-actions .primary-button').trigger('click');
    expect(wrapper.emitted('generate-all')).toEqual([[[{ video: { path: '/videos/lesson.mp4', filename: 'lesson.mp4', cachedPairs: [['zh-CN', 'vi']] }, source: 'zh-CN', target: 'vi' }]]]);
  });
});
