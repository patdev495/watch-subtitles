<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { FolderOpen, MonitorPlay } from 'lucide-vue-next';
import PlayerControls from './PlayerControls.vue';

const props = withDefaults(defineProps<{
  src?: string;
  filename?: string;
  initialTime?: number;
  hasPrevious?: boolean;
  hasNext?: boolean;
}>(), { hasPrevious: false, hasNext: false });

const emit = defineEmits<{
  (e: 'timeupdate', time: number): void;
  (e: 'durationchange', duration: number): void;
  (e: 'play'): void;
  (e: 'pause'): void;
  (e: 'open-file'): void;
  (e: 'ended'): void;
  (e: 'error'): void;
  (e: 'previous'): void;
  (e: 'next'): void;
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
/* The dock sits below the stage, so it only auto-hides once it overlays the video. */
const dockHidden = computed(() => isFullscreen.value && !showControls.value);

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
    <div class="player-stage">
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

        <!-- Empty state -->
        <div v-else class="empty-hero">
          <div class="empty-content">
            <span class="empty-icon" aria-hidden="true"><MonitorPlay :size="26" :stroke-width="1.5" /></span>
            <p class="hero-title">Kéo &amp; Thả Video Vào Đây</p>
            <p class="hero-subtitle">hoặc chọn một tệp từ máy của bạn</p>
            <button class="browse-btn" @click.stop="emit('open-file')">
              <FolderOpen :size="16" :stroke-width="2" aria-hidden="true" />
              <span>Mở video</span>
            </button>
          </div>
        </div>
      </div>

      <slot :is-fullscreen="isFullscreen" :controls-visible="showControls || !isPlaying" />
    </div>

    <!-- Transport dock: below the stage, or overlaid on it in fullscreen -->
    <div v-if="src" class="transport-dock" :class="{ 'dock-idle': dockHidden }">
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
        :has-previous="hasPrevious"
        :has-next="hasNext"
        @toggle-play="togglePlay"
        @seek="onSeek"
        @seek-relative="seekRelative"
        @toggle-mute="toggleMute"
        @volume-change="onVolumeChange"
        @playback-rate-change="changePlaybackRate"
        @fullscreen="toggleFullscreen"
        @previous="emit('previous')"
        @next="emit('next')"
      />
    </div>
  </div>
</template>

<style scoped>
.player-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
}

.player-card:fullscreen {
  gap: 0;
  background: var(--bg-player);
}

/* ── Stage ──────────────────────────────────────────────────────────────── */
.player-stage {
  position: relative;
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  border-radius: 0;
  background: var(--bg-player);
  border: 0;
  box-shadow: none;
}

.player-card:fullscreen .player-stage {
  border: 0;
  border-radius: 0;
  box-shadow: none;
}

.viewport {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: var(--bg-player);
  cursor: pointer;
}

.video-core {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* ── Empty state ────────────────────────────────────────────────────────── */
.empty-hero {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  padding: var(--space-6);
  border: 0;
  border-radius: 0;
  background: var(--bg-surface);
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  text-align: center;
}

.empty-icon {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  margin-bottom: var(--space-3);
  border-radius: var(--radius-panel);
  background: var(--accent-soft);
  color: var(--accent);
}

.hero-title {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--font-display);
  font-weight: 600;
}

.hero-subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--font-body);
}

.browse-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  height: var(--control-height-lg);
  margin-top: var(--space-4);
  padding: 0 var(--space-5);
  border: 1px solid var(--accent);
  border-radius: var(--radius-control);
  background: var(--accent);
  color: var(--accent-contrast);
  font-size: var(--font-body);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.browse-btn:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

/* ── Transport dock ─────────────────────────────────────────────────────── */
.transport-dock {
  flex: 0 0 auto;
  padding: var(--space-2) var(--space-4) var(--space-3);
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  opacity: 1;
  transition: opacity var(--transition-base), transform var(--transition-base);
}

.player-card:fullscreen .transport-dock {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 10;
  padding: var(--space-8) var(--space-5) var(--space-4);
  border: 0;
  background: var(--player-scrim);
}

.transport-dock.dock-idle {
  opacity: 0;
  transform: translateY(10px);
  pointer-events: none;
}
</style>
