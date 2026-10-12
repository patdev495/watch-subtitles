<script setup lang="ts">
import { Play, Pause, Volume2, VolumeX, Maximize, RotateCcw, RotateCw, SkipBack, SkipForward } from 'lucide-vue-next';

withDefaults(defineProps<{
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  playbackRate: number;
  progressPercent: number;
  formattedCurrentTime: string;
  formattedDuration: string;
  hasPrevious?: boolean;
  hasNext?: boolean;
}>(), { hasPrevious: false, hasNext: false });

const emit = defineEmits<{
  (e: 'toggle-play'): void;
  (e: 'seek', value: number): void;
  (e: 'seek-relative', delta: number): void;
  (e: 'toggle-mute'): void;
  (e: 'volume-change', value: number): void;
  (e: 'playback-rate-change', rate: number): void;
  (e: 'fullscreen'): void;
  (e: 'previous'): void;
  (e: 'next'): void;
}>();

const PLAYBACK_RATES = [0.5, 0.75, 1, 1.25, 1.5, 2] as const;
function onSeek(event: Event): void { emit('seek', parseFloat((event.target as HTMLInputElement).value)); }
function onVolumeChange(event: Event): void { emit('volume-change', parseFloat((event.target as HTMLInputElement).value)); }
function onRateChange(event: Event): void { emit('playback-rate-change', parseFloat((event.target as HTMLSelectElement).value)); }
</script>

<template>
  <div class="transport">
    <div class="progress-row">
      <span class="time-current">{{ formattedCurrentTime }}</span>
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
      <span class="time-total">{{ formattedDuration }}</span>
    </div>

    <div class="controls-row">
      <div class="controls-group">
        <button
          class="icon-btn"
          title="Video trước"
          aria-label="Video trước"
          :disabled="!hasPrevious"
          @click.stop="emit('previous')"
        >
          <SkipBack :size="18" :stroke-width="1.75" aria-hidden="true" />
        </button>
        <button class="icon-btn" title="Lùi 10s (←)" aria-label="Lùi 10 giây" @click.stop="emit('seek-relative', -10)">
          <RotateCcw :size="18" :stroke-width="1.75" aria-hidden="true" />
        </button>
        <button
          class="icon-btn play-toggle-btn"
          :title="isPlaying ? 'Tạm dừng (Space)' : 'Phát (Space)'"
          :aria-label="isPlaying ? 'Tạm dừng' : 'Phát'"
          @click.stop="emit('toggle-play')"
        >
          <Pause v-if="isPlaying" :size="20" :stroke-width="2" aria-hidden="true" />
          <Play v-else :size="20" :stroke-width="2" aria-hidden="true" class="play-icon-offset" />
        </button>
        <button class="icon-btn" title="Tiến 10s (→)" aria-label="Tiến 10 giây" @click.stop="emit('seek-relative', 10)">
          <RotateCw :size="18" :stroke-width="1.75" aria-hidden="true" />
        </button>
        <button
          class="icon-btn"
          title="Video kế tiếp"
          aria-label="Video kế tiếp"
          :disabled="!hasNext"
          @click.stop="emit('next')"
        >
          <SkipForward :size="18" :stroke-width="1.75" aria-hidden="true" />
        </button>
      </div>

      <div class="controls-group controls-right">
        <div class="volume-box">
          <button class="icon-btn" :title="isMuted ? 'Bật âm' : 'Tắt âm'" :aria-label="isMuted ? 'Bật âm' : 'Tắt âm'" @click.stop="emit('toggle-mute')">
            <VolumeX v-if="isMuted || volume === 0" :size="18" :stroke-width="1.75" aria-hidden="true" />
            <Volume2 v-else :size="18" :stroke-width="1.75" aria-hidden="true" />
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
          <Maximize :size="18" :stroke-width="1.75" aria-hidden="true" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.transport {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  width: 100%;
  min-width: 0;
  user-select: none;
}

/* ── Timeline ───────────────────────────────────────────────────────────── */
.progress-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.timeline-box {
  position: relative;
  flex: 1;
  min-width: var(--space-10);
  height: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.timeline-track {
  width: 100%;
  height: var(--progress-height);
  border-radius: var(--radius-pill);
  background: var(--bg-active);
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
  background: var(--accent);
  position: relative;
}

.timeline-thumb {
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%) scale(0);
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent-hover);
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

.time-current,
.time-total {
  flex: 0 0 auto;
  font-size: var(--font-meta);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.time-current {
  color: var(--text-primary);
  font-weight: 600;
}

.time-total {
  color: var(--text-muted);
}

/* ── Buttons ────────────────────────────────────────────────────────────── */
.controls-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.controls-group {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  min-width: 0;
}

.controls-group:first-child {
  grid-column: 2;
}

.controls-right {
  grid-column: 3;
  justify-self: end;
  gap: var(--space-2);
}

.icon-btn {
  flex: 0 0 auto;
  width: var(--player-control-size);
  height: var(--player-control-size);
  display: grid;
  place-items: center;
  padding: 0;
  border: 1px solid transparent;
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-subtle);
  color: var(--text-primary);
}

.icon-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.play-toggle-btn {
  width: calc(var(--player-control-size) + 6px);
  height: calc(var(--player-control-size) + 6px);
  margin: 0 var(--space-1);
  border-radius: 50%;
  background: var(--accent);
  border-color: var(--accent);
  color: var(--accent-contrast);
}

.play-toggle-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
  color: var(--accent-contrast);
}

.play-icon-offset {
  margin-left: 2px;
}

/* ── Volume & speed ─────────────────────────────────────────────────────── */
.volume-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.vol-slider {
  width: var(--volume-width);
  height: var(--progress-height);
  cursor: pointer;
}

.speed-select-wrapper {
  display: flex;
  align-items: center;
}

.speed-select {
  height: 30px;
  padding: 0 var(--space-2);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: var(--bg-raised);
  color: var(--text-primary);
  font-size: var(--font-meta);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  cursor: pointer;
  outline: none;
  transition: border-color var(--transition-fast), background-color var(--transition-fast);
}

.speed-select:hover {
  background: var(--bg-hover);
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
  .controls-row {
    display: flex;
    justify-content: space-between;
  }

  .time-total {
    display: none;
  }
}
</style>
