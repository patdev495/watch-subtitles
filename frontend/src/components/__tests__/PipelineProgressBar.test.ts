import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import PipelineProgressBar from '../PipelineProgressBar.vue';
import type { PipelineStatus } from '../../types';

describe('PipelineProgressBar', () => {
  const baseStatus: PipelineStatus = {
    status: 'running',
    progress: 35,
    step: 'Đang nhận diện giọng nói (STT)...',
    cues: [],
    error: null,
  };

  it('renders progress percentage and step label during execution', () => {
    const wrapper = mount(PipelineProgressBar, {
      props: {
        modelValue: true,
        status: baseStatus,
      },
    });

    expect(wrapper.text()).toContain('35%');
    expect(wrapper.text()).toContain('Đang nhận diện giọng nói (STT)...');
    expect(wrapper.text()).toContain('Đang Xử Lý Phụ Đề Tự Động');
  });

  it('displays error message when status is error', () => {
    const errorStatus: PipelineStatus = {
      status: 'error',
      progress: 25,
      step: 'Lỗi',
      cues: [],
      error: 'Invalid API key',
    };

    const wrapper = mount(PipelineProgressBar, {
      props: {
        modelValue: true,
        status: errorStatus,
      },
    });

    expect(wrapper.text()).toContain('Lỗi Tạo Phụ Đề');
    expect(wrapper.text()).toContain('Invalid API key');
  });

  it('displays completed state when finished', () => {
    const completedStatus: PipelineStatus = {
      status: 'completed',
      progress: 100,
      step: 'Hoàn thành!',
      cues: [],
      error: null,
    };

    const wrapper = mount(PipelineProgressBar, {
      props: {
        modelValue: true,
        status: completedStatus,
      },
    });

    expect(wrapper.text()).toContain('Tạo Phụ Đề Hoàn Tất!');
    expect(wrapper.text()).toContain('100%');
  });
});
