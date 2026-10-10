import { describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import App from '../App.vue';
import TranscriptFooter from '../components/TranscriptFooter.vue';
import VideoPlayer from '../components/VideoPlayer.vue';
import type { PyWebViewApi } from '../types';

describe('App', () => {
  it('clears Playback Queue, stops the player, persists empty state, and leaves Subtitle Jobs running', async () => {
    const paths = ['/videos/a.mp4', '/videos/b.mp4'];
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok' }),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: paths.map((path) => ({ path, source_language: 'en' })), selected_path: paths[0], playback_time: 23, auto_advance: true }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [] }),
      load_video_path: vi.fn().mockResolvedValue({ cancelled: false, path: paths[0], filename: 'a.mp4', stream_url: 'http://localhost/a' }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: false, cues: [] }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [{ id: 'running', video_path: paths[0], source_language: 'en', target_language: 'vi', status: 'processing', progress: 30, step: '', cues: [], error: null, cached: false }] }),
      save_playback_queue: vi.fn().mockResolvedValue({}),
      remove_subtitle_job: vi.fn(),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { props: ['src'], template: '<div data-test="player" />' } } } });
    await flushPromises();
    expect(wrapper.findAll('.playback-queue li')).toHaveLength(2);
    await wrapper.get('button[aria-label="Xóa tất cả video khỏi hàng đợi phát"]').trigger('click');
    await flushPromises();

    expect(wrapper.findAll('.playback-queue li')).toHaveLength(0);
    expect(wrapper.findComponent(VideoPlayer).props('src')).toBe('');
    expect(api.save_playback_queue).toHaveBeenLastCalledWith({ videos: [], selected_path: '', playback_time: 0, auto_advance: true });
    expect(api.remove_subtitle_job).not.toHaveBeenCalled();
    wrapper.unmount();
  });
  it('creates eligible jobs in Playback Queue order from modal', async () => {
    const paths = ['/a.mp4', '/b.mp4', '/c.mp4'];
    const create = vi.fn().mockImplementation(async (path: string) => ({ ok: true, job: {
      id: path, video_path: path, source_language: 'en', target_language: 'vi', status: 'waiting', progress: 0, step: '', cues: [], error: null, cached: false,
    } }));
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok' }), list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      get_settings: vi.fn().mockResolvedValue({ default_target_language: 'vi' }),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: paths.map((path) => ({ path, source_language: 'en' })), selected_path: '', playback_time: 0, auto_advance: true }),
      get_cached_subtitle_languages: vi.fn().mockImplementation(async (path: string) => ({ ok: true, language_pairs: path === '/a.mp4' ? [['en', 'vi']] : [] })),
      save_playback_queue: vi.fn().mockResolvedValue({}), create_subtitle_job: create,
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div />' } } } });
    await flushPromises();
    await wrapper.get('button[aria-label="Phụ đề"]').trigger('click');
    await wrapper.get('.modal-actions button').trigger('click');
    await flushPromises();
    expect(create.mock.calls.map((call) => call[0])).toEqual(['/b.mp4', '/c.mp4']);
    wrapper.unmount();
  });
  it('restores display preferences and saves changes through bridge API', async () => {
    const preferences = {
      primary_line: 'original' as const, overlay_visible: false,
      lines: {
        original: { visible: true, font_size: 27 }, translated: { visible: true, font_size: 18 },
        originalPinyin: { visible: true, font_size: 15 }, translatedPinyin: { visible: true, font_size: 15 },
      },
    };
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok' }),
      get_settings: vi.fn().mockResolvedValue({ default_target_language: 'vi' }),
      get_subtitle_display_preferences: vi.fn().mockResolvedValue(preferences),
      save_subtitle_display_preferences: vi.fn().mockResolvedValue(preferences),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: [{ path: '/a.mp4', source_language: 'en' }], selected_path: '/a.mp4', playback_time: 0, auto_advance: true }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [['en', 'vi']] }),
      load_video_path: vi.fn().mockResolvedValue({ cancelled: false, path: '/a.mp4', filename: 'a.mp4', stream_url: 'http://localhost/a' }),
      get_latest_cached_subtitles: vi.fn().mockResolvedValue({ cached: true, source_language: 'en', target_language: 'vi', cues: [{ id: '1', start: 0, end: 2, originalText: 'Original', translatedText: 'Translated' }] }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      save_playback_queue: vi.fn().mockResolvedValue({}),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div><slot :is-fullscreen="false" :controls-visible="true" /></div>' } } } });
    await flushPromises();
    wrapper.findComponent(VideoPlayer).vm.$emit('timeupdate', 1);
    await flushPromises();
    expect(wrapper.find('.caption-card').exists()).toBe(false);
    await wrapper.get('button[aria-label="Hiện phụ đề"]').trigger('click');
    await flushPromises();
    expect(api.save_subtitle_display_preferences).toHaveBeenCalledWith(expect.objectContaining({ primary_line: 'original', overlay_visible: true }));
    wrapper.unmount();
  });
  it('opens Subtitle Generation Modal without leaving the playback workspace', async () => {
    window.pywebview = undefined;
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div data-test="player" />' } } } });
    await wrapper.get('button[aria-label="Phụ đề"]').trigger('click');
    expect(wrapper.find('[role="dialog"][aria-label="Tạo phụ đề"]').exists()).toBe(true);
    expect(wrapper.find('[aria-label="Playback Queue"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="player"]').exists()).toBe(true);
    wrapper.unmount();
  });
  it('ignores duplicate imports and reports the Vietnamese message', async () => {
    const entry = { cancelled: false, path: '/videos/a.mp4', filename: 'a.mp4', stream_url: 'http://localhost/a' };
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: [], selected_path: '', playback_time: 0, auto_advance: true }),
      open_video_files_dialog: vi.fn().mockResolvedValue({ cancelled: false, videos: [entry, entry] }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [] }),
      save_playback_queue: vi.fn().mockResolvedValue({}),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div />' } } } });
    await flushPromises();
    await wrapper.get('.queue-imports button').trigger('click');
    await flushPromises();
    expect(wrapper.findAll('.playback-queue li')).toHaveLength(1);
    expect(wrapper.text()).toContain('Video đã trong hàng đợi rồi.');
  });
  it('restores queue when desktop bridge becomes ready after mounting', async () => {
    window.pywebview = undefined;
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div />' } } } });
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      get_settings: vi.fn().mockResolvedValue({}),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: [{ path: '/videos/a.mp4', source_language: 'en' }], selected_path: '', playback_time: 0, auto_advance: true }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [] }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    window.dispatchEvent(new Event('pywebviewready'));
    await flushPromises();
    expect(wrapper.findAll('.playback-queue li')).toHaveLength(1);
    wrapper.unmount();
  });
  it('restores selected video, playback time, source language, and auto-advance choice', async () => {
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: [{ path: '/videos/a.mp4', source_language: 'zh-CN' }], selected_path: '/videos/a.mp4', playback_time: 31, auto_advance: false }),
      load_video_path: vi.fn().mockResolvedValue({ cancelled: false, path: '/videos/a.mp4', filename: 'a.mp4', stream_url: 'http://localhost/a' }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [] }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: false, cues: [] }),
      save_playback_queue: vi.fn().mockResolvedValue({}),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { props: ['initialTime'], template: '<div data-test="player" />' } } } });
    await flushPromises();
    expect(wrapper.get('[data-test="queue-row-active"]').text()).toContain('a.mp4');
    expect((wrapper.get('.playback-queue .source select').element as HTMLSelectElement).value).toBe('zh-CN');
    expect((wrapper.get('.auto-advance input').element as HTMLInputElement).checked).toBe(false);
    expect(wrapper.findComponent(VideoPlayer).props('initialTime')).toBe(31);
  });
  it('auto-advances past unavailable video and leaves it marked in queue', async () => {
    const paths = ['/videos/a.mp4', '/videos/b.mp4', '/videos/c.mp4'];
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: paths.map((path) => ({ path, source_language: 'en' })), selected_path: paths[0], playback_time: 0, auto_advance: true }),
      load_video_path: vi.fn().mockImplementation(async (path: string) => path === paths[1] ? { cancelled: true } : { cancelled: false, path, filename: path.split('/').pop(), stream_url: `http://localhost/${path}` }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [] }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: false, cues: [] }),
      save_playback_queue: vi.fn().mockResolvedValue({}),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div data-test="player"><slot :is-fullscreen="false" :controls-visible="true" /></div>' } } } });
    await flushPromises();
    wrapper.findComponent(VideoPlayer).vm.$emit('ended');
    await flushPromises();
    expect(wrapper.get('[data-test="queue-row-active"]').text()).toContain('c.mp4');
    expect(wrapper.text()).toContain('Không thể phát video.');
    expect(wrapper.findAll('.playback-queue li')).toHaveLength(3);
  });
  it('loads newest cached subtitle pair when selecting a video', async () => {
    const cues = [{ id: 'new', start: 0, end: 2, originalText: 'Hej', translatedText: 'Hi' }];
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      open_video_dialog: vi.fn().mockResolvedValue({ cancelled: false, path: '/videos/a.mp4', filename: 'a.mp4', stream_url: 'http://localhost/a' }),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [['en', 'vi'], ['zh-CN', 'en']] }),
      get_latest_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: true, source_language: 'zh-CN', target_language: 'en', cues }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: false, cues: [] }),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div><slot :is-fullscreen="false" :controls-visible="true" /></div>' } } } });
    await wrapper.get('button.open-button').trigger('click');
    await flushPromises();
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual(cues);
    expect(wrapper.findComponent(TranscriptFooter).props('sourceLanguage')).toBe('zh-CN');
  });
  it('keeps queue beside player and selects next video after removing active video', async () => {
    const video = (name: string) => ({ cancelled: false, path: `/videos/${name}.mp4`, filename: `${name}.mp4`, stream_url: `http://localhost/${name}` });
    const api = {
      ping: vi.fn().mockResolvedValue({ status: 'ok', message: 'ready' }),
      list_subtitle_jobs: vi.fn().mockResolvedValue({ ok: true, jobs: [] }),
      get_playback_queue: vi.fn().mockResolvedValue({ videos: [], selected_path: '', playback_time: 0, auto_advance: true }),
      save_playback_queue: vi.fn().mockResolvedValue({}),
      open_video_files_dialog: vi.fn().mockResolvedValue({ cancelled: false, videos: [video('a'), video('b')] }),
      load_video_path: vi.fn().mockImplementation(async (path: string) => video(path.includes('/a.') ? 'a' : 'b')),
      get_cached_subtitle_languages: vi.fn().mockResolvedValue({ ok: true, language_pairs: [] }),
      get_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: false, cues: [] }),
    } as unknown as PyWebViewApi;
    window.pywebview = { api };
    const wrapper = mount(App, { global: { stubs: { VideoPlayer: { template: '<div data-test="player"><slot :is-fullscreen="false" :controls-visible="true" /></div>' } } } });
    await flushPromises();

    expect(wrapper.find('[aria-label="Playback Queue"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="player"]').exists()).toBe(true);
    await wrapper.get('.queue-imports button').trigger('click');
    await flushPromises();
    expect(wrapper.findAll('.playback-queue li')).toHaveLength(2);
    await wrapper.get('[data-test="queue-select-a"]').trigger('click');
    await flushPromises();
    await wrapper.get('[data-test="queue-remove-a"]').trigger('click');
    await flushPromises();
    expect(wrapper.findAll('.playback-queue li')).toHaveLength(1);
    expect(wrapper.get('[data-test="queue-row-active"]').text()).toContain('b.mp4');
    expect(api.save_playback_queue).toHaveBeenCalled();
  });
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
      get_latest_cached_subtitles: vi.fn().mockResolvedValue({ ok: true, cached: true, source_language: 'auto', target_language: 'vi', cues: cachedCues }),
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

    await wrapper.get('button.open-button').trigger('click');
    await flushPromises();

    expect(api.get_latest_cached_subtitles).toHaveBeenCalledWith('C:/videos/queued.mp4');
    expect(wrapper.findComponent(TranscriptFooter).props('sourceLanguage')).toBe('auto');
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

    await wrapper.get('button.open-button').trigger('click');
    await flushPromises();
    await wrapper.get('.playback-queue .source select').setValue('auto');
    await wrapper.get('[data-test="queue-select-q"]').trigger('click');
    await flushPromises();

    expect(api.get_cached_subtitles).toHaveBeenCalledWith('C:/videos/queued.mp4', 'auto', 'vi');
    expect((wrapper.get('.playback-queue .source select').element as HTMLSelectElement).value).toBe('auto');
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
    await wrapper.get('.playback-queue .source select').setValue('auto');
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
    await wrapper.get('button[aria-label="Phụ đề"]').trigger('click');
    await wrapper.get('[data-test="generate-video"]').trigger('click');
    await flushPromises();

    expect(api.create_subtitle_job).toHaveBeenCalledWith('C:/videos/cached.mp4', 'en', 'vi', true);
    expect(wrapper.findComponent(TranscriptFooter).props('cues')).toEqual(cachedCues);
  });
});
