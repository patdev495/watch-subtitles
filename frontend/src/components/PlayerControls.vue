<script setup lang="ts">
import { Play, Pause, Volume2, VolumeX, Maximize, RotateCcw, RotateCw } from 'lucide-vue-next';

defineProps<{
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  playbackRate: number;
  progressPercent: number;
  formattedCurrentTime: string;
  formattedDuration: string;
}>();

const emit = defineEmits<{
  (e: 'toggle-play'): void;
  (e: 'seek', value: number): void;
  (e: 'seek-relative', delta: number): void;
  (e: 'toggle-mute'): void;
  (e: 'volume-change', value: number): void;
  (e: 'playback-rate-change', rate: number): void;
  (e: 'fullscreen'): void;
}>();

const PLAYBACK_RATES = [0.5, 0.75, 1, 1.25, 1.5, 2] as const;
function onSeek(event: Event): void { emit('seek', parseFloat((event.target as HTMLInputElement).value)); }
function onVolumeChange(event: Event): void { emit('volume-change', parseFloat((event.target as HTMLInputElement).value)); }
function onRateChange(event: Event): void { emit('playback-rate-change', parseFloat((event.target as HTMLSelectElement).value)); }
</script>

<template>
  <div class="actions-strip">
    <button
      class="icon-btn play-toggle-btn"
      :title="isPlaying ? 'Tạm dừng (Space)' : 'Phát (Space)'"
      :aria-label="isPlaying ? 'Tạm dừng' : 'Phát'"
      @click.stop="emit('toggle-play')"
    >
      <Pause v-if="isPlaying" :size="17" :stroke-width="2" aria-hidden="true" />
      <Play v-else :size="17" :stroke-width="2" aria-hidden="true" class="play-icon-offset" />
    </button>
    <button class="icon-btn" title="Lùi 10s (←)" aria-label="Lùi 10 giây" @click.stop="emit('seek-relative', -10)">
      <RotateCcw :size="16" :stroke-width="1.75" aria-hidden="true" />
    </button>
    <button class="icon-btn" title="Tiến 10s (→)" aria-label="Tiến 10 giây" @click.stop="emit('seek-relative', 10)">
      <RotateCw :size="16" :stroke-width="1.75" aria-hidden="true" />
    </button>
    <div class="timeline-box">
      <div class="timeline-track">
        <div class="timeline-fill" :style="{ width: `${progressPercent}%` }">
          <span class="timeline-thumb"></span>
        </div>
      </div>
      <input
        type="range"
        min="0"
        :max="duration || 100"
        step="0.05"
        :value="currentTime"
        class="timeline-slider"
        aria-label="Tiến trình video"
        @input="onSeek"
      />
    </div>
    <div class="time-counter">
      <span class="time-current">{{ formattedCurrentTime }}</span>
      <span class="divider">/</span>
      <span class="time-total">{{ formattedDuration }}</span>
    </div>
    <div class="volume-box">
      <button class="icon-btn" :title="isMuted ? 'Bật âm' : 'Tắt âm'" :aria-label="isMuted ? 'Bật âm' : 'Tắt âm'" @click.stop="emit('toggle-mute')">
        <VolumeX v-if="isMuted || volume === 0" :size="17" :stroke-width="1.75" aria-hidden="true" />
        <Volume2 v-else :size="17" :stroke-width="1.75" aria-hidden="true" />
      </button>
      <input
        type="range"
        min="0"
        max="1"
        step="0.05"
        :value="isMuted ? 0 : volume"
        class="vol-slider"
        aria-label="Âm lượng"
        @input="onVolumeChange"
      />
    </div>
    <div class="speed-select-wrapper">
      <select :value="playbackRate" class="speed-select" aria-label="Tốc độ phát" @change="onRateChange">
        <option v-for="r in PLAYBACK_RATES" :key="r" :value="r">{{ r }}x</option>
      </select>
    </div>
    <button class="icon-btn" title="Toàn màn hình" aria-label="Toàn màn hình" @click.stop="emit('fullscreen')">
      <Maximize :size="16" :stroke-width="1.75" aria-hidden="true" />
    </button>
  </div>
</template>

<style scoped>
.actions-strip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  min-width: 0;
  padding: 0 var(--space-2);
  user-select: none;
}

.icon-btn {
  flex: 0 0 var(--player-control-size);
  width: var(--player-control-size);
  height: var(--player-control-size);
  display: grid;
  place-items: center;
  padding: 0;
  border: 1px solid transparent;
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
}

.play-toggle-btn {
  background: #ffffff;
  color: #09090b;
  border-color: #ffffff;
  box-shadow: none;
}

.play-toggle-btn:hover {
  background: #e4e4e7;
  border-color: #e4e4e7;
  transform: scale(1.04);
}

.play-icon-offset {
  margin-left: 1px;
}

.timeline-box {
  position: relative;
  flex: 1;
  min-width: var(--space-10);
  height: var(--player-control-size);
  display: flex;
  align-items: center;
  margin: 0 var(--space-2);
  cursor: pointer;
}

.timeline-track {
  width: 100%;
  height: var(--progress-height);
  overflow: visible;
  border-radius: var(--radius-pill);
  background: #27272a;
  transition: height var(--transition-fast);
  position: relative;
}

.timeline-box:hover .timeline-track,
.timeline-box:focus-within .timeline-track {
  height: var(--progress-hover-height);
}

.timeline-fill {
  height: 100%;
  border-radius: var(--radius-pill);
  background: #ffffff;
  position: relative;
}

.timeline-thumb {
  position: absolute;
  right: -5px;
  top: 50%;
  transform: translateY(-50%) scale(0);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
  transition: transform var(--transition-fast);
}

.timeline-box:hover .timeline-thumb,
.timeline-box:focus-within .timeline-thumb {
  transform: translateY(-50%) scale(1);
}

.timeline-slider {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  margin: 0;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.time-counter {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 3px;
  color: var(--text-secondary);
  font-size: var(--font-meta);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.time-current {
  color: var(--text-primary);
  font-weight: 500;
}

.divider {
  color: var(--text-muted);
}

.volume-box {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.vol-slider {
  width: var(--volume-width);
  height: var(--progress-height);
  cursor: pointer;
}

.speed-select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.speed-select {
  height: 28px;
  padding: 0 var(--space-2);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: var(--font-meta);
  font-weight: 500;
  cursor: pointer;
  outline: none;
  transition: border-color var(--transition-fast), background-color var(--transition-fast);
}

.speed-select:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--border-strong);
}

.speed-select:focus-visible {
  border-color: var(--border-focus);
}

@media (max-width: 1100px) {
  .volume-box .vol-slider {
    display: none;
  }
}

@media (max-width: 900px) {
  .actions-strip {
    gap: var(--space-1);
  }
  .timeline-box {
    margin: 0 var(--space-1);
  }
}
</style>
