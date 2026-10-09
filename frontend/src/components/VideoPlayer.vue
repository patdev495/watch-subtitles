<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  RotateCcw,
  RotateCw,
  UploadCloud,
  FileVideo
} from 'lucide-vue-next';

const props = defineProps<{
  src?: string;
  filename?: string;
}>();

const emit = defineEmits<{
  (e: 'timeupdate', time: number): void;
  (e: 'durationchange', duration: number): void;
  (e: 'play'): void;
  (e: 'pause'): void;
  (e: 'open-file'): void;
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(1);
const isMuted = ref(false);
const playbackRate = ref(1);
const isFullscreen = ref(false);
const playerContainer = ref<HTMLDivElement | null>(null);
const showControls = ref(true);
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
const progressPercent = computed(() => {
  if (!duration.value || duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

function togglePlay() {
  if (!videoRef.value || !props.src) return;
  if (videoRef.value.paused) {
    videoRef.value.play();
  } else {
    videoRef.value.pause();
  }
}

function handleTimeUpdate() {
  if (!videoRef.value) return;
  currentTime.value = videoRef.value.currentTime;
  emit('timeupdate', currentTime.value);
}

function handleLoadedMetadata() {
  if (!videoRef.value) return;
  duration.value = videoRef.value.duration;
  emit('durationchange', duration.value);
}

function onSeek(event: Event) {
  const target = event.target as HTMLInputElement;
  const time = parseFloat(target.value);
  if (videoRef.value) {
    videoRef.value.currentTime = time;
    currentTime.value = time;
  }
}

function seekRelative(delta: number) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = Math.max(0, Math.min(duration.value, videoRef.value.currentTime + delta));
}

function seekTo(time: number) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = time;
  currentTime.value = time;
}

function toggleMute() {
  if (!videoRef.value) return;
  isMuted.value = !isMuted.value;
  videoRef.value.muted = isMuted.value;
}

function onVolumeChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const val = parseFloat(target.value);
  volume.value = val;
  if (videoRef.value) {
    videoRef.value.volume = val;
    videoRef.value.muted = val === 0;
    isMuted.value = val === 0;
  }
}

function changePlaybackRate(rate: number) {
  playbackRate.value = rate;
  if (videoRef.value) {
    videoRef.value.playbackRate = rate;
  }
}

function toggleFullscreen() {
  if (!playerContainer.value) return;
  if (!document.fullscreenElement) {
    playerContainer.value.requestFullscreen().then(() => {
      isFullscreen.value = true;
    }).catch(console.error);
  } else {
    document.exitFullscreen().then(() => {
      isFullscreen.value = false;
    }).catch(console.error);
  }
}

function handleMouseMove() {
  showControls.value = true;
  if (hideControlsTimeout) clearTimeout(hideControlsTimeout);
  if (isPlaying.value) {
    hideControlsTimeout = window.setTimeout(() => {
      showControls.value = false;
    }, 3000);
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.code === 'Space') {
    event.preventDefault();
    togglePlay();
  } else if (event.code === 'ArrowLeft') {
    event.preventDefault();
    seekRelative(-5);
  } else if (event.code === 'ArrowRight') {
    event.preventDefault();
    seekRelative(5);
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  if (hideControlsTimeout) clearTimeout(hideControlsTimeout);
});

defineExpose({
  seekTo
});
</script>

<template>
  <div
    ref="playerContainer"
    class="player-card"
    @mousemove="handleMouseMove"
    @mouseleave="isPlaying && (showControls = false)"
  >
    <!-- Viewport Area -->
    <div class="viewport" @click="togglePlay">
      <video
        v-if="src"
        ref="videoRef"
        :src="src"
        class="video-core"
        @timeupdate="handleTimeUpdate"
        @loadedmetadata="handleLoadedMetadata"
        @play="isPlaying = true; emit('play')"
        @pause="isPlaying = false; emit('pause')"
      ></video>

      <!-- Empty State / Hero Upload -->
      <div v-else class="empty-hero">
        <div class="empty-content">
          <div class="icon-halo">
            <UploadCloud :size="40" class="upload-icon" />
          </div>
          <h2 class="hero-title">Kéo & Thả Video Vào Đây</h2>
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

    <!-- Floating Cinema Controls (Visible when media loaded) -->
    <div
      v-if="src"
      class="controls-scrim"
      :class="{ 'controls-visible': showControls || !isPlaying }"
    >
      <!-- Timeline Scrubber with buffered gradient track -->
      <div class="timeline-box">
        <div class="timeline-track">
          <div class="timeline-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
        <input
          type="range"
          min="0"
          :max="duration || 100"
          step="0.05"
          :value="currentTime"
          class="timeline-slider"
          @input="onSeek"
        />
      </div>

      <!-- Controls Action Bar -->
      <div class="actions-strip">
        <!-- Left: Play/Pause, Replay/Forward, Timecode -->
        <div class="left-strip">
          <button
            class="play-toggle-btn"
            :title="isPlaying ? 'Tạm dừng (Space)' : 'Phát (Space)'"
            @click.stop="togglePlay"
          >
            <Pause v-if="isPlaying" :size="20" class="icon-white" />
            <Play v-else :size="20" class="icon-white" style="margin-left: 2px" />
          </button>

          <button class="icon-btn" title="Lùi 5s (←)" @click.stop="seekRelative(-5)">
            <RotateCcw :size="16" />
          </button>
          <button class="icon-btn" title="Tiến 5s (→)" @click.stop="seekRelative(5)">
            <RotateCw :size="16" />
          </button>

          <div class="time-counter">
            <span class="curr-time">{{ formattedCurrentTime }}</span>
            <span class="divider">/</span>
            <span class="total-time">{{ formattedDuration }}</span>
          </div>
        </div>

        <!-- Right: Volume, Speed, Fullscreen -->
        <div class="right-strip">
          <!-- Volume Hover Pill -->
          <div class="volume-box">
            <button class="icon-btn" @click.stop="toggleMute">
              <VolumeX v-if="isMuted || volume === 0" :size="18" />
              <Volume2 v-else :size="18" />
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              :value="isMuted ? 0 : volume"
              class="vol-slider"
              @input="onVolumeChange"
            />
          </div>

          <!-- Speed Dropdown -->
          <div class="speed-box">
            <select
              :value="playbackRate"
              class="speed-select"
              @change="changePlaybackRate(parseFloat(($event.target as HTMLSelectElement).value))"
            >
              <option :value="0.5">0.5x</option>
              <option :value="0.75">0.75x</option>
              <option :value="1">1.0x</option>
              <option :value="1.25">1.25x</option>
              <option :value="1.5">1.5x</option>
              <option :value="2">2.0x</option>
            </select>
          </div>

          <!-- Fullscreen -->
          <button class="icon-btn" title="Toàn màn hình" @click.stop="toggleFullscreen">
            <Maximize :size="18" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.player-card {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 380px;
  background: #020617;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
}

.viewport {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.video-core {
  width: 100%;
  height: 100%;
  max-height: 60vh;
  object-fit: contain;
}

/* Empty State Styling */
.empty-hero {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, #0f172a 0%, #020617 80%);
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
  border-radius: 24px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
}

.upload-icon {
  color: #38bdf8;
}

.hero-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #f8fafc;
  margin-bottom: 8px;
}

.hero-subtitle {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 24px;
}

.browse-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border-radius: 9999px;
  background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%);
  color: #ffffff;
  font-weight: 600;
  font-size: 13px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  transition: all 0.2s ease;
}

.browse-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.6);
}

/* Floating Cinema Controls */
.controls-scrim {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(2, 6, 23, 0.95) 0%, rgba(2, 6, 23, 0.6) 65%, transparent 100%);
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

/* Timeline Scrubber */
.timeline-box {
  position: relative;
  width: 100%;
  height: 20px;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  cursor: pointer;
}

.timeline-track {
  position: absolute;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.timeline-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #38bdf8);
  border-radius: 9999px;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.7);
}

.timeline-slider {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

/* Action Strip */
.actions-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-strip, .right-strip {
  display: flex;
  align-items: center;
  gap: 12px;
}

.play-toggle-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px rgba(99, 102, 241, 0.5);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.play-toggle-btn:hover {
  transform: scale(1.08);
  filter: brightness(1.1);
}

.icon-white {
  color: #ffffff;
}

.icon-btn {
  background: transparent;
  border: none;
  color: #cbd5e1;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #38bdf8;
}

.time-counter {
  font-family: var(--font-mono);
  font-size: 13px;
  display: flex;
  gap: 6px;
  color: #e2e8f0;
  background: rgba(15, 23, 42, 0.6);
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.time-counter .divider {
  color: #64748b;
}

.time-counter .total-time {
  color: #94a3b8;
}

/* Volume */
.volume-box {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(15, 23, 42, 0.6);
  padding: 2px 8px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.vol-slider {
  width: 65px;
  height: 4px;
}

/* Speed */
.speed-box .speed-select {
  background: rgba(15, 23, 42, 0.6);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}
</style>
