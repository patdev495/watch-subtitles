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
    <button class="icon-btn play-toggle-btn" :title="isPlaying ? 'Tạm dừng (Space)' : 'Phát (Space)'" :aria-label="isPlaying ? 'Tạm dừng' : 'Phát'" @click.stop="emit('toggle-play')">
      <Pause v-if="isPlaying" :size="18" :stroke-width="1.5" aria-hidden="true" /><Play v-else :size="18" :stroke-width="1.5" aria-hidden="true" />
    </button>
    <button class="icon-btn" title="Lùi 10s (←)" aria-label="Lùi 10 giây" @click.stop="emit('seek-relative', -10)"><RotateCcw :size="16" :stroke-width="1.5" aria-hidden="true" /></button>
    <button class="icon-btn" title="Tiến 10s (→)" aria-label="Tiến 10 giây" @click.stop="emit('seek-relative', 10)"><RotateCw :size="16" :stroke-width="1.5" aria-hidden="true" /></button>
    <div class="timeline-box">
      <div class="timeline-track"><div class="timeline-fill" :style="{ width: `${progressPercent}%` }" /></div>
      <input type="range" min="0" :max="duration || 100" step="0.05" :value="currentTime" class="timeline-slider" aria-label="Tiến trình video" @input="onSeek" />
    </div>
    <div class="time-counter"><span>{{ formattedCurrentTime }}</span><span class="divider">/</span><span>{{ formattedDuration }}</span></div>
    <div class="volume-box">
      <button class="icon-btn" :title="isMuted ? 'Bật âm' : 'Tắt âm'" :aria-label="isMuted ? 'Bật âm' : 'Tắt âm'" @click.stop="emit('toggle-mute')"><VolumeX v-if="isMuted || volume === 0" :size="18" :stroke-width="1.5" aria-hidden="true" /><Volume2 v-else :size="18" :stroke-width="1.5" aria-hidden="true" /></button>
      <input type="range" min="0" max="1" step="0.05" :value="isMuted ? 0 : volume" class="vol-slider" aria-label="Âm lượng" @input="onVolumeChange" />
    </div>
    <select :value="playbackRate" class="speed-select" aria-label="Tốc độ phát" @change="onRateChange"><option v-for="r in PLAYBACK_RATES" :key="r" :value="r">{{ r }}x</option></select>
    <button class="icon-btn" title="Toàn màn hình" aria-label="Toàn màn hình" @click.stop="emit('fullscreen')"><Maximize :size="18" :stroke-width="1.5" aria-hidden="true" /></button>
  </div>
</template>

<style scoped>
.actions-strip { display: flex; align-items: center; gap: var(--space-1); width: 100%; min-width: 0; }
.icon-btn { flex: 0 0 var(--player-control-size); width: var(--player-control-size); height: var(--player-control-size); display: grid; place-items: center; padding: 0; border: 0; border-radius: var(--radius-control); background: transparent; color: var(--text-primary); cursor: pointer; }
.icon-btn:hover { background: var(--bg-overlay); }
.timeline-box { position: relative; flex: 1; min-width: var(--space-10); height: var(--player-control-size); display: flex; align-items: center; margin: 0 var(--space-2); }
.timeline-track { width: 100%; height: var(--progress-height); overflow: hidden; border-radius: var(--radius-sm); background: var(--text-muted); transition: height var(--transition-fast); }
.timeline-box:hover .timeline-track, .timeline-box:focus-within .timeline-track { height: var(--progress-hover-height); }
.timeline-fill { height: 100%; border-radius: var(--radius-sm); background: var(--accent-primary); }
.timeline-slider { position: absolute; inset: 0; width: 100%; height: 100%; margin: 0; opacity: 0; cursor: pointer; }
.time-counter { display: flex; flex: 0 0 auto; gap: var(--space-1); color: var(--text-primary); font-size: var(--font-body); font-variant-numeric: tabular-nums; white-space: nowrap; }
.divider { color: var(--text-secondary); }
.volume-box { display: flex; align-items: center; gap: var(--space-1); }
.vol-slider { width: var(--volume-width); height: var(--progress-height); }
.speed-select { height: var(--control-height); padding: 0 var(--space-1); border: 0; border-radius: var(--radius-control); background: transparent; color: var(--text-primary); font-size: var(--font-meta); cursor: pointer; }
.speed-select:hover { background: var(--bg-overlay); }
@media (max-width: 1100px) { .volume-box .vol-slider { display: none; } }
@media (max-width: 900px) { .actions-strip { gap: 0; } .timeline-box { margin: 0 var(--space-1); } }
</style>
