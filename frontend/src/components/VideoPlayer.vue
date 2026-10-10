<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { FileVideo } from 'lucide-vue-next';
import PlayerControls from './PlayerControls.vue';

const props = defineProps<{
  src?: string;
  filename?: string;
  initialTime?: number;
}>();

const emit = defineEmits<{
  (e: 'timeupdate', time: number): void;
  (e: 'durationchange', duration: number): void;
  (e: 'play'): void;
  (e: 'pause'): void;
  (e: 'open-file'): void;
  (e: 'ended'): void;
  (e: 'error'): void;
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const playerContainer = ref<HTMLDivElement | null>(null);
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(1);
const isMuted = ref(false);
const playbackRate = ref(1);
const showControls = ref(true);
const isFullscreen = ref(false);
let hideControlsTimeout: number | null = null;

function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return '00:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const hrs = Math.floor(mins / 60);
  if (hrs > 0) {
    const remMins = mins % 60;
    return `${hrs.toString().padStart(2, '0')}:${remMins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

const formattedCurrentTime = computed(() => formatTime(currentTime.value));
const formattedDuration = computed(() => formatTime(duration.value));
const progressPercent = computed(() =>
  duration.value ? (currentTime.value / duration.value) * 100 : 0
);

function togglePlay() {
  if (!videoRef.value || !props.src) return;
  videoRef.value.paused ? videoRef.value.play() : videoRef.value.pause();
}

function handleTimeUpdate() {
  if (!videoRef.value) return;
  currentTime.value = videoRef.value.currentTime;
  emit('timeupdate', currentTime.value);
}

function handleLoadedMetadata() {
  if (!videoRef.value) return;
  if (props.initialTime) videoRef.value.currentTime = props.initialTime;
  duration.value = videoRef.value.duration;
  emit('durationchange', duration.value);
}

watch(() => props.src, async (src) => {
  if (!src) return;
  await nextTick();
  if (videoRef.value) void videoRef.value.play().catch(() => { /* browser may block automatic playback */ });
});

function onSeek(time: number) {
  if (videoRef.value) {
    videoRef.value.currentTime = time;
    currentTime.value = time;
    emit('timeupdate', time);
  }
}

function seekRelative(delta: number) {
  if (!videoRef.value) return;
  const nextTime = Math.max(0, Math.min(duration.value, videoRef.value.currentTime + delta));
  videoRef.value.currentTime = nextTime;
  currentTime.value = nextTime;
  emit('timeupdate', nextTime);
}

function seekTo(time: number) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = time;
  currentTime.value = time;
  emit('timeupdate', time);
}

function toggleMute() {
  if (!videoRef.value) return;
  isMuted.value = !isMuted.value;
  videoRef.value.muted = isMuted.value;
}

function onVolumeChange(val: number) {
  volume.value = val;
  if (videoRef.value) {
    videoRef.value.volume = val;
    videoRef.value.muted = val === 0;
    isMuted.value = val === 0;
  }
}

function changePlaybackRate(rate: number) {
  playbackRate.value = rate;
  if (videoRef.value) videoRef.value.playbackRate = rate;
}

function toggleFullscreen() {
  if (!playerContainer.value) return;
  if (!document.fullscreenElement) {
    playerContainer.value.requestFullscreen().then(() => { /* noop */ }).catch(console.error);
  } else {
    document.exitFullscreen().catch(console.error);
  }
}

function handleMouseMove() {
  showControls.value = true;
  if (hideControlsTimeout) clearTimeout(hideControlsTimeout);
  if (isPlaying.value) {
    hideControlsTimeout = window.setTimeout(() => { showControls.value = false; }, 2500);
  }
}

function handleFullscreenChange(): void {
  isFullscreen.value = document.fullscreenElement === playerContainer.value;
  showControls.value = true;
}

function handleKeydown(event: KeyboardEvent) {
  if (event.code === 'Space') { event.preventDefault(); togglePlay(); }
  else if (event.code === 'ArrowLeft') { event.preventDefault(); seekRelative(-5); }
  else if (event.code === 'ArrowRight') { event.preventDefault(); seekRelative(5); }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
  document.addEventListener('fullscreenchange', handleFullscreenChange);
});
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  document.removeEventListener('fullscreenchange', handleFullscreenChange);
  if (hideControlsTimeout) clearTimeout(hideControlsTimeout);
});

defineExpose({ seekTo });
</script>

<template>
  <div
    ref="playerContainer"
    class="player-card"
    @mousemove="handleMouseMove"
    @touchstart.passive="handleMouseMove"
    @mouseleave="isPlaying && (showControls = false)"
  >
    <!-- Viewport -->
    <div class="viewport" @click="togglePlay">
      <video
        v-if="src"
        ref="videoRef"
        :src="src"
        autoplay
        class="video-core"
        @timeupdate="handleTimeUpdate"
        @loadedmetadata="handleLoadedMetadata"
        @play="isPlaying = true; emit('play')"
        @pause="isPlaying = false; emit('pause')"
        @ended="emit('ended')"
        @error="emit('error')"
      />

      <!-- Empty State -->
      <div v-else class="empty-hero">
        <div class="empty-content">
          <FileVideo :size="18" :stroke-width="1.5" class="upload-icon" aria-hidden="true" />
          <p class="hero-subtitle">Kéo &amp; Thả Video Vào Đây</p>
          <button class="browse-btn" @click.stop="emit('open-file')">
            <FileVideo :size="16" :stroke-width="1.5" aria-hidden="true" />
            <span>Mở video</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Cinema Controls -->
    <div
      v-if="src"
      class="controls-scrim"
      :class="{ 'controls-visible': showControls || !isPlaying }"
    >
      <PlayerControls
        :is-playing="isPlaying"
        :current-time="currentTime"
        :duration="duration"
        :volume="volume"
        :is-muted="isMuted"
        :playback-rate="playbackRate"
        :progress-percent="progressPercent"
        :formatted-current-time="formattedCurrentTime"
        :formatted-duration="formattedDuration"
        @toggle-play="togglePlay"
        @seek="onSeek"
        @seek-relative="seekRelative"
        @toggle-mute="toggleMute"
        @volume-change="onVolumeChange"
        @playback-rate-change="changePlaybackRate"
        @fullscreen="toggleFullscreen"
      />
    </div>
    <slot :is-fullscreen="isFullscreen" :controls-visible="showControls || !isPlaying" />
  </div>
</template>

<style scoped>
.player-card { position: relative; display: flex; flex-direction: column; width: 100%; height: 100%; min-width: 0; min-height: 0; overflow: hidden; background: var(--bg-player); }
.player-card:fullscreen { width: 100vw; height: 100vh; }
.viewport { position: relative; display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; background: var(--bg-player); cursor: pointer; }
.video-core { width: 100%; height: 100%; object-fit: contain; }
.empty-hero { position: absolute; inset: 0; display: grid; place-items: center; padding: var(--space-8); background: var(--bg-base); }
.empty-content { display: flex; flex-direction: column; align-items: center; gap: var(--space-4); text-align: center; }
.upload-icon { color: var(--text-secondary); }
.hero-subtitle { margin: 0; color: var(--text-secondary); font-size: var(--font-body); }
.browse-btn { display: inline-flex; align-items: center; gap: var(--space-2); height: var(--control-height); padding: 0 var(--space-3); border: 0; border-radius: var(--radius-control); background: var(--accent-primary); color: var(--accent-contrast); font-size: var(--font-body); font-weight: 500; cursor: pointer; }
.browse-btn:hover { opacity: .88; }
.controls-scrim { position: absolute; right: 0; bottom: 0; left: 0; z-index: 10; padding: var(--space-6) var(--space-4) var(--space-3); background: var(--player-scrim); opacity: 0; transition: opacity var(--transition-fast); pointer-events: none; }
.controls-scrim.controls-visible, .controls-scrim:focus-within { opacity: 1; pointer-events: auto; }
</style>
