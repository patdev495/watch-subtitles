import { describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import App from '../App.vue';
import TranscriptFooter from '../components/TranscriptFooter.vue';
import type { PyWebViewApi } from '../types';

describe('App', () => {
  it('shows no subtitle cue when a desktop video has no cached subtitles', async () => {
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      open_video_dialog: vi.fn().mockResolvedValue({
        cancelled: false,
        path: 'C:/videos/uncached.mp4',
        filename: 'uncached.mp4',
        stream_url: 'http://localhost/stream?path=uncached.mp4',
      }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [] }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: false, cues: [] }),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };

    const wrapper = mount(App, {
      global: {
        stubs: {
          VideoPlayer: {
            template: '<div><slot :is-fullscreen="false" :controls-visible="true" /></div>',
          },
        },
      },
    });
    await wrapper.get('button.open-button').trigger('click');
    await flushPromises();

    expect(api.get_cached_subtitles).toHaveBeenCalledWith('C:/videos/uncached.mp4', 'en', 'vi');
    expect(wrapper.text()).toContain('uncached.mp4');
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual([]);
    expect(wrapper.text()).not.toContain('Hello, welcome to the video player.');
  });

  it('loads auto-detected cached cues when opening a video for playback', async () => {
    const cachedCues = [{ id: '1', start: 0, end: 2, originalText: 'Hello', translatedText: 'Xin chào' }];
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      open_video_dialog: vi.fn().mockResolvedValue({
        cancelled: false,
        path: 'C:/videos/queued.mp4',
        filename: 'queued.mp4',
        stream_url: 'http://localhost/stream?path=queued.mp4',
      }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [['auto', 'vi']] }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: true, cues: cachedCues }),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };

    const wrapper = mount(App, {
      global: {
        stubs: {
          VideoPlayer: {
            template: '<div><slot :is-fullscreen="false" :controls-visible="true" /></div>',
          },
        },
      },
    });

    await wrapper.get('#source-language').setValue('auto');
    await wrapper.get('button.open-button').trigger('click');
    await flushPromises();

    expect(api.get_cached_subtitles).toHaveBeenCalledWith('C:/videos/queued.mp4', 'auto', 'vi');
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual(cachedCues);
  });

  it('opens a queued video with its selected subtitle language pair', async () => {
    const autoCues = [{ id: '1', start: 0, end: 2, originalText: '你好', translatedText: 'Xin chào' }];
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      open_video_dialog: vi.fn().mockResolvedValue({
        cancelled: false,
        path: 'C:/videos/queued.mp4',
        filename: 'queued.mp4',
        stream_url: 'http://localhost/stream?path=queued.mp4',
      }),
      load_video_path: vi.fn().mockResolvedValue({
        cancelled: false,
        path: 'C:/videos/queued.mp4',
        filename: 'queued.mp4',
        stream_url: 'http://localhost/stream?path=queued.mp4',
      }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [['auto', 'vi']] }),
      get_cached_subtitles: vi.fn().mockImplementation(async (_path: string, source: string) => ({
        ok: true,
        cached: source === 'auto',
        cues: source === 'auto' ? autoCues : [],
      })),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, {
      global: { stubs: { VideoPlayer: { template: '<div><slot :is-fullscreen="false" :controls-visible="true" /></div>' } } },
    });

    await wrapper.get('button.queue-button').trigger('click');
    await wrapper.get('.queue-actions .secondary-button').trigger('click');
    await flushPromises();
    await wrapper.get('[data-test="source-language"]').setValue('auto');
    await wrapper.get('[data-test="play-video"]').trigger('click');
    await flushPromises();

    expect(api.get_cached_subtitles).toHaveBeenCalledWith('C:/videos/queued.mp4', 'auto', 'vi');
    expect((wrapper.get('#source-language').element as HTMLSelectElement).value).toBe('auto');
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual(autoCues);
  });

  it('reloads subtitles when the player source language changes', async () => {
    const autoCues = [{ id: 'auto-1', start: 0, end: 2, originalText: '你好', translatedText: 'Xin chào' }];
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      open_video_dialog: vi.fn().mockResolvedValue({
        cancelled: false, path: 'C:/videos/queued.mp4', filename: 'queued.mp4',
        stream_url: 'http://localhost/stream?path=queued.mp4',
      }),
      get_cached_subtitles: vi.fn().mockImplementation(async (_path: string, source: string) => ({
        ok: true, cached: source === 'auto', cues: source === 'auto' ? autoCues : [],
      })),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, {
      global: { stubs: { VideoPlayer: { template: '<div><slot :is-fullscreen="false" :controls-visible="true" /></div>' } } },
    });

    await wrapper.get('button.open-button').trigger('click');
    await flushPromises();
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual([]);
    await wrapper.get('#source-language').setValue('auto');
    await flushPromises();

    expect(api.get_cached_subtitles).toHaveBeenCalledWith('C:/videos/queued.mp4', 'auto', 'vi');
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual(autoCues);
  });

  it('forces regeneration for the current cached language pair from the player', async () => {
    const cachedCues = [{ id: '1', start: 0, end: 2, originalText: 'Old', translatedText: 'Cũ' }];
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      open_video_dialog: vi.fn().mockResolvedValue({
        cancelled: false,
        path: 'C:/videos/cached.mp4',
        filename: 'cached.mp4',
        stream_url: 'http://localhost/stream?path=cached.mp4',
      }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [['en', 'vi']] }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: true, cues: cachedCues }),
      create_subtitle_job: vi.fn().mockResolvedValue({
        ok: true,
        job: { id: 'fresh-job', video_path: 'C:/videos/cached.mp4', source_language: 'en', target_language: 'vi', status: 'waiting', progress: 0, step: 'waiting', cues: [], error: null, cached: false },
      }),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };

    const wrapper = mount(App, {
      global: { stubs: { VideoPlayer: { template: '<div><slot :is-fullscreen="false" :controls-visible="true" /></div>' } } },
    });
    await wrapper.get('button.open-button').trigger('click');
    await flushPromises();
    await wrapper.get('button.generate-button').trigger('click');
    await flushPromises();

    expect(api.create_subtitle_job).toHaveBeenCalledWith('C:/videos/cached.mp4', 'en', 'vi', true);
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual([]);
  });
});
