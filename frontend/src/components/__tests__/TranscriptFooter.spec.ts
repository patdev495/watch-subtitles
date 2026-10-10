import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import TranscriptFooter from '../TranscriptFooter.vue';

describe('TranscriptFooter', () => {
  it('restores display choices and emits updates from Sub and Aa controls', async () => {
    const preferences = {
      primary_line: 'original' as const, overlay_visible: false,
      lines: {
        original: { visible: true, font_size: 27 }, translated: { visible: false, font_size: 30 },
        originalPinyin: { visible: true, font_size: 15 }, translatedPinyin: { visible: true, font_size: 15 },
      },
    };
    const wrapper = mount(TranscriptFooter, { props: {
      cues: [{ id: '1', start: 0, end: 2, originalText: 'Original', translatedText: 'Translated' }],
      currentTime: 1, sourceLanguage: 'en', targetLanguage: 'vi', preferences,
    } });
    expect(wrapper.find('.caption-card').exists()).toBe(false);
    await wrapper.get('button[aria-label="Mở chỉnh phụ đề"]').trigger('click');
    expect(wrapper.get('input[aria-label="Cỡ chữ dòng Gốc"]').element).toHaveProperty('value', '27');
    expect(wrapper.get('.detail-line--translated').attributes('style')).toContain('display: none');
    await wrapper.get('button[aria-label="Hiện phụ đề"]').trigger('click');
    expect(wrapper.emitted('update:preferences')?.at(-1)?.[0]).toMatchObject({ primary_line: 'original', overlay_visible: true });
  });
  it('shows only cue active at current playback time', () => {
    const wrapper = mount(TranscriptFooter, {
      props: {
        cues: [
          { id: '1', start: 0, end: 2, originalText: 'First', translatedText: 'Đầu tiên' },
          { id: '2', start: 2, end: 4, originalText: 'Second', translatedText: 'Thứ hai' },
        ],
        currentTime: 2.5,
        sourceLanguage: 'en',
        targetLanguage: 'vi',
      },
    });

    expect(wrapper.text()).toContain('Thứ hai');
    expect(wrapper.text()).not.toContain('Đầu tiên');
  });

  it('keeps the on-video subtitle text selectable without an info icon', () => {
    const wrapper = mount(TranscriptFooter, {
      props: {
        cues: [{ id: '1', start: 0, end: 2, originalText: 'Select this', translatedText: 'Chọn câu này' }],
        currentTime: 1,
        sourceLanguage: 'en',
        targetLanguage: 'vi',
      },
    });

    expect(wrapper.get('.caption-card').element.tagName).toBe('DIV');
    expect(wrapper.get('.caption-text').text()).toBe('Chọn câu này');
    expect(wrapper.get('.caption-original').text()).toBe('Select this');
    expect(wrapper.find('button[aria-label="Mở chi tiết phụ đề"]').exists()).toBe(false);
  });

  it('marks original and translated text in the detail panel as selectable', async () => {
    const wrapper = mount(TranscriptFooter, {
      props: {
        cues: [{ id: '1', start: 0, end: 2, originalText: 'Hello, my friend.', translatedText: 'Xin chào, bạn của tớ.' }],
        currentTime: 1,
        sourceLanguage: 'en',
        targetLanguage: 'vi',
      },
    });

    await wrapper.get('.caption-card').trigger('click');
    expect(wrapper.get('.detail-line--original .selectable-detail-text').text()).toBe('Hello, my friend.');
    expect(wrapper.get('.detail-line--translated .selectable-detail-text').text()).toBe('Xin chào, bạn của tớ.');
  });

  it('shows tone-marked pinyin beneath Chinese text', async () => {
    const wrapper = mount(TranscriptFooter, {
      props: {
        cues: [{ id: '1', start: 0, end: 2, originalText: '你好', translatedText: 'Hello' }],
        currentTime: 1,
        sourceLanguage: 'zh-CN',
        targetLanguage: 'en',
      },
    });

    await wrapper.get('.caption-card').trigger('click');
    expect(wrapper.text()).toContain('nǐ hǎo');
  });

  it('lets viewers hide a line and change its font size', async () => {
    const wrapper = mount(TranscriptFooter, {
      props: {
        cues: [{ id: '1', start: 0, end: 2, originalText: 'Original', translatedText: 'Translated' }],
        currentTime: 1,
        sourceLanguage: 'en',
        targetLanguage: 'vi',
      },
    });

    await wrapper.get('.caption-card').trigger('click');
    await wrapper.get('button[aria-label="Mở chỉnh phụ đề"]').trigger('click');
    await wrapper.get('button[aria-label="Ẩn dòng Gốc"]').trigger('click');
    expect(wrapper.get('.detail-line--original').attributes('style')).toContain('display: none');

    await wrapper.get('input[aria-label="Cỡ chữ dòng Dịch"]').setValue('28');
    expect(wrapper.get('.detail-line--translated p').attributes('style')).toContain('28px');
  });

  it('shows the original and translation when opening display settings from the toolbar', async () => {
    const wrapper = mount(TranscriptFooter, {
      props: {
        cues: [{ id: '1', start: 0, end: 2, originalText: 'Original', translatedText: 'Translated' }],
        currentTime: 1,
        sourceLanguage: 'en',
        targetLanguage: 'vi',
      },
    });

    await wrapper.get('button[aria-label="Ẩn phụ đề"]').trigger('click');
    expect(wrapper.find('.caption-card').exists()).toBe(false);
    expect(wrapper.find('button[aria-label="Hiện phụ đề"]').exists()).toBe(true);

    await wrapper.get('button[aria-label="Mở chỉnh phụ đề"]').trigger('click');
    expect(wrapper.find('[aria-label="Chi tiết phụ đề hiện tại"]').exists()).toBe(true);
    expect(wrapper.get('.detail-line--original .selectable-detail-text').text()).toBe('Original');
    expect(wrapper.get('.detail-line--translated .selectable-detail-text').text()).toBe('Translated');

    await wrapper.get('button[aria-label="Hiển thị dòng gốc trên video"]').trigger('click');
    await wrapper.get('button[aria-label="Hiện phụ đề"]').trigger('click');
    expect(wrapper.get('.caption-card').text()).toContain('Original');
  });
});
