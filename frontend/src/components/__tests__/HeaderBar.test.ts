import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import HeaderBar from '../HeaderBar.vue';

describe('HeaderBar', () => {
  it('offers automatic language detection as a source language', () => {
    const wrapper = mount(HeaderBar, {
      props: { backendConnected: true },
    });

    expect(wrapper.get('#source-language').text()).toContain('Tự động phát hiện');
  });
});
