<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { UploadCloud, FileVideo } from 'lucide-vue-next';
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
    hideControlsTimeout = window.setTimeout(() => { showControls.value = false; }, 3000);
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
          <div class="icon-halo">
            <UploadCloud :size="40" class="upload-icon" />
          </div>
          <h2 class="hero-title">Kéo &amp; Thả Video Vào Đây</h2>
          <p class="hero-subtitle">
            Hỗ trợ MP4, MKV, WebM, MOV với tốc độ xử lý âm thanh bản địa qua FFmpeg
          </p>
          <button class="browse-btn" @click.stop="emit('open-file')">
            <FileVideo :size="16" />
            <span>Chọn video từ máy</span>
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
.player-card {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 380px;
  background: var(--bg-player);
  border-radius: var(--radius-card);
  overflow: hidden;
  box-shadow: var(--shadow-panel);
  border: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
}

.player-card:fullscreen { width: 100vw; height: 100vh; border: 0; border-radius: 0; }

.viewport {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.video-core {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* Empty State */
.empty-hero {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-player);
  padding: 40px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 480px;
}

.icon-halo {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-card);
  background: var(--accent-soft);
  border: 1px solid var(--border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: none;
}

.upload-icon { color: var(--accent-hover); }

.hero-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.hero-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 24px;
}

.browse-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border-radius: var(--radius-control);
  background: var(--accent-primary);
  color: var(--accent-contrast);
  font-weight: 600;
  font-size: 13px;
  border: none;
  cursor: pointer;
  box-shadow: none;
  transition: background-color var(--transition-fast);
}

.browse-btn:hover {
  background: var(--accent-hover);
}

/* Floating Cinema Controls */
.controls-scrim {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--player-scrim);
  padding: 24px 20px 14px;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.3s ease, transform 0.3s ease;
  pointer-events: none;
}

.controls-scrim.controls-visible {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
</style>
