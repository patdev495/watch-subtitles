import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import SettingsModal from '../SettingsModal.vue';

describe('SettingsModal', () => {
  it('offers Google Translate without an API key', async () => {
    const wrapper = mount(SettingsModal, {
      props: { modelValue: true, initialSettings: { deepgram_api_key: '', deepl_api_key: '', default_target_language: 'vi', stt_provider: 'deepgram', translation_provider: 'deepl' } },
      global: { stubs: { Teleport: true } },
    });

    await wrapper.get('#translation-provider').setValue('google');

    expect(wrapper.text()).toContain('Google Translate không cần API key.');
    expect(wrapper.find('#deepl-key').exists()).toBe(false);
  });
});
