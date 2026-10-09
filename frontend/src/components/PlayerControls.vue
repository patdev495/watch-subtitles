<script setup lang="ts">
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  RotateCcw,
  RotateCw,
} from 'lucide-vue-next';

const props = defineProps<{
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

function onSeek(event: Event) {
  const val = parseFloat((event.target as HTMLInputElement).value);
  emit('seek', val);
}

function onVolumeChange(event: Event) {
  const val = parseFloat((event.target as HTMLInputElement).value);
  emit('volume-change', val);
}

function onRateChange(event: Event) {
  const val = parseFloat((event.target as HTMLSelectElement).value);
  emit('playback-rate-change', val);
}
</script>

<template>
  <!-- Timeline Scrubber -->
  <div class="timeline-box">
    <div class="timeline-track">
      <div class="timeline-fill" :style="{ width: `${progressPercent}%` }" />
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

  <!-- Actions Strip -->
  <div class="actions-strip">
    <!-- Left: Play/Pause, Replay/Forward, Timecode -->
    <div class="left-strip">
      <button
        class="play-toggle-btn"
        :title="isPlaying ? 'Tạm dừng (Space)' : 'Phát (Space)'"
        @click.stop="emit('toggle-play')"
      >
        <Pause v-if="isPlaying" :size="20" class="icon-white" />
        <Play v-else :size="20" class="icon-white" style="margin-left: 2px" />
      </button>

      <button class="icon-btn" title="Lùi 5s (←)" @click.stop="emit('seek-relative', -5)">
        <RotateCcw :size="16" />
      </button>
      <button class="icon-btn" title="Tiến 5s (→)" @click.stop="emit('seek-relative', 5)">
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
      <div class="volume-box">
        <button class="icon-btn" @click.stop="emit('toggle-mute')">
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

      <div class="speed-box">
        <select :value="playbackRate" class="speed-select" @change="onRateChange">
          <option v-for="r in PLAYBACK_RATES" :key="r" :value="r">{{ r }}x</option>
        </select>
      </div>

      <button class="icon-btn" title="Toàn màn hình" @click.stop="emit('fullscreen')">
        <Maximize :size="18" />
      </button>
    </div>
  </div>
</template>

<style scoped>
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

.left-strip,
.right-strip {
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
