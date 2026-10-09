import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import TranscriptFooter from '../TranscriptFooter.vue';

describe('TranscriptFooter', () => {
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

  it('shows tone-marked pinyin beneath Chinese text', async () => {
    const wrapper = mount(TranscriptFooter, {
      props: {
        cues: [{ id: '1', start: 0, end: 2, originalText: '你好', translatedText: 'Hello' }],
        currentTime: 1,
        sourceLanguage: 'zh-CN',
        targetLanguage: 'en',
      },
    });

    await wrapper.get('button[aria-label="Mở chi tiết phụ đề"]').trigger('click');
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

    await wrapper.get('button[aria-label="Mở chi tiết phụ đề"]').trigger('click');
    await wrapper.get('button[aria-label="Mở chỉnh phụ đề"]').trigger('click');
    await wrapper.get('button[aria-label="Ẩn dòng Gốc"]').trigger('click');
    expect(wrapper.get('.detail-line--original').attributes('style')).toContain('display: none');

    await wrapper.get('input[aria-label="Cỡ chữ dòng Dịch"]').setValue('28');
    expect(wrapper.get('.detail-line--translated p').attributes('style')).toContain('28px');
  });

  it('keeps a persistent subtitle visibility control and opens compact display settings', async () => {
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
    expect(wrapper.find('[aria-label="Chỉnh hiển thị phụ đề"]').exists()).toBe(true);

    await wrapper.get('button[aria-label="Hiển thị dòng gốc trên video"]').trigger('click');
    await wrapper.get('button[aria-label="Hiện phụ đề"]').trigger('click');
    expect(wrapper.get('.caption-card').text()).toContain('Original');
  });
});
