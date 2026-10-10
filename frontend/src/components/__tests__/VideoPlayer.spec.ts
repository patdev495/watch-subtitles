import { describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import VideoPlayer from '../VideoPlayer.vue';

describe('VideoPlayer', () => {
  it('requests fullscreen on player container and resumes saved playback time', async () => {
    const wrapper = mount(VideoPlayer, { props: { src: 'http://localhost/video.mp4', initialTime: 31 } });
    const player = wrapper.get('.player-card').element as HTMLElement;
    const requestFullscreen = vi.fn().mockResolvedValue(undefined);
    player.requestFullscreen = requestFullscreen;
    await wrapper.get('video').trigger('loadedmetadata');
    expect((wrapper.get('video').element as HTMLVideoElement).currentTime).toBe(31);
    await wrapper.get('[title="Toàn màn hình"]').trigger('click');
    expect(requestFullscreen).toHaveBeenCalledOnce();
  });
  it('emits the new playback position immediately when the viewer seeks', async () => {
    const wrapper = mount(VideoPlayer, {
      props: { src: 'http://localhost/video.mp4' },
    });

    await wrapper.get('input.timeline-slider').setValue(12.5);

    expect(wrapper.emitted('timeupdate')).toEqual([[12.5]]);
  });
});
