import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import SubtitleGenerationModal from '../SubtitleGenerationModal.vue';

describe('SubtitleGenerationModal', () => {
  it('shows one row per video with independently editable source and target languages', async () => {
    const videos = [
      { path: '/folder-a/1.mp4', filename: '1.mp4', sourceLanguage: 'en', cachedPairs: [] },
      { path: '/folder-b/1.mp4', filename: '1.mp4', sourceLanguage: 'en', cachedPairs: [] },
      { path: '/videos/2.mp4', filename: '2.mp4', sourceLanguage: 'en', cachedPairs: [] },
    ];
    const wrapper = mount(SubtitleGenerationModal, { props: {
      open: true, videos, jobs: [], defaultTargetLanguage: 'vi', activePath: videos[0].path,
    } });
    const rows = wrapper.findAll('.modal-row');
    expect(rows).toHaveLength(3);
    expect(wrapper.find('.active-language-pair').exists()).toBe(false);
    for (const row of rows) {
      expect(row.findAll('[data-test="source-language"]')).toHaveLength(1);
      expect(row.findAll('[data-test="target-language"]')).toHaveLength(1);
    }

    await rows[1]!.get('[data-test="source-language"]').setValue('zh-CN');
    await rows[2]!.get('[data-test="target-language"]').setValue('zh-TW');
    await wrapper.get('.modal-actions button').trigger('click');
    expect(wrapper.emitted('generate-all')?.[0]?.[0]).toEqual([
      { video: videos[0], source: 'en', target: 'vi', force: false },
      { video: videos[1], source: 'zh-CN', target: 'vi', force: false },
      { video: videos[2], source: 'en', target: 'zh-TW', force: false },
    ]);
  });

  it('creates a job for one video with its edited language pair', async () => {
    const video = { path: '/videos/lesson.mp4', filename: 'lesson.mp4', sourceLanguage: 'en', cachedPairs: [] };
    const wrapper = mount(SubtitleGenerationModal, { props: { open: true, videos: [video], jobs: [], defaultTargetLanguage: 'vi' } });

    await wrapper.get('[data-test="source-language"]').setValue('zh-CN');
    expect(wrapper.emitted('source-change')).toEqual([[video, 'zh-CN']]);
    await wrapper.get('[data-test="target-language"]').setValue('en');
    await wrapper.get('[data-test="generate-video"]').trigger('click');

    expect(wrapper.emitted('generate')).toEqual([[video, 'zh-CN', 'en', false]]);
  });
  it('creates only uncached inactive pairs in Playback Queue order', async () => {
    const videos = [
      { path: '/a.mp4', filename: 'a.mp4', sourceLanguage: 'en', cachedPairs: [['en', 'vi']] as [string, string][] },
      { path: '/b.mp4', filename: 'b.mp4', sourceLanguage: 'en', cachedPairs: [] as [string, string][] },
      { path: '/c.mp4', filename: 'c.mp4', sourceLanguage: 'en', cachedPairs: [] as [string, string][] },
      { path: '/d.mp4', filename: 'd.mp4', sourceLanguage: 'en', cachedPairs: [] as [string, string][] },
    ];
    const jobs = [{ id: 'active', video_path: '/c.mp4', source_language: 'en', target_language: 'vi', status: 'waiting' as const, progress: 0, step: '', cues: [], error: null, cached: false }];
    const wrapper = mount(SubtitleGenerationModal, { props: { open: true, videos, jobs, defaultTargetLanguage: 'vi' } });
    await wrapper.get('.modal-actions button').trigger('click');
    expect(wrapper.emitted('generate-all')).toEqual([[[
      { video: videos[1], source: 'en', target: 'vi', force: false },
      { video: videos[3], source: 'en', target: 'vi', force: false },
    ]]]);
  });
  it('shows background progress after reopening and blocks a matching duplicate', async () => {
    const video = { path: '/a.mp4', filename: 'a.mp4', sourceLanguage: 'en', cachedPairs: [] };
    const waiting = { id: 'job', video_path: video.path, source_language: 'en', target_language: 'vi', status: 'waiting' as const, progress: 0, step: '', cues: [], error: null, cached: false };
    const wrapper = mount(SubtitleGenerationModal, { props: { open: true, videos: [video], jobs: [waiting], defaultTargetLanguage: 'vi' } });
    expect(wrapper.text()).toContain('Đang chờ');
    expect(wrapper.get('[data-test="generate-video"]').attributes('disabled')).toBeDefined();
    await wrapper.setProps({ open: false, jobs: [{ ...waiting, status: 'processing', progress: 47 }] });
    await wrapper.setProps({ open: true });
    expect(wrapper.text()).toContain('47%');
  });

  it('retries a failed job using its original pair', async () => {
    const video = { path: '/a.mp4', filename: 'a.mp4', sourceLanguage: 'en', cachedPairs: [] };
    const failed = { id: 'failed', video_path: video.path, source_language: 'en', target_language: 'vi', status: 'failed' as const, progress: 22, step: '', cues: [], error: 'offline', cached: false };
    const wrapper = mount(SubtitleGenerationModal, { props: { open: true, videos: [video], jobs: [failed], defaultTargetLanguage: 'vi' } });
    expect(wrapper.text()).toContain('Thất bại');
    await wrapper.get('[data-test="retry-job"]').trigger('click');
    expect(wrapper.emitted('retry')).toEqual([['failed']]);
  });
});
