import { describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import VideoPlayer from '../VideoPlayer.vue';

describe('VideoPlayer', () => {
  it('emits the new playback position immediately when the viewer seeks', async () => {
    const wrapper = mount(VideoPlayer, {
      props: { src: 'http://localhost/video.mp4' },
    });

    await wrapper.get('input.timeline-slider').setValue(12.5);

    expect(wrapper.emitted('timeupdate')).toEqual([[12.5]]);
  });
});
