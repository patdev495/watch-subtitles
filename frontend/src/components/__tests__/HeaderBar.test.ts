import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import HeaderBar from '../HeaderBar.vue';

describe('HeaderBar', () => {
  it('opens Subtitle Generation Modal from its single subtitle action', async () => {
    const wrapper = mount(HeaderBar, {
      props: { backendConnected: true },
    });

    expect(wrapper.find('.language-control').exists()).toBe(false);
    expect(wrapper.find('.queue-button').exists()).toBe(false);
    expect(wrapper.find('.generate-button').exists()).toBe(false);
    await wrapper.get('button[aria-label="Phụ đề"]').trigger('click');
    expect(wrapper.emitted('open-subtitles')).toHaveLength(1);
  });
});
