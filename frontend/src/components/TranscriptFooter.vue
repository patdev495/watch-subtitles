<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import type { Cue } from '../types';
import { useTranscript } from '../composables/useTranscript';

const props = defineProps<{
  cues: Cue[];
  currentTime: number;
}>();

const emit = defineEmits<{
  (e: 'seek', time: number): void;
}>();

const cuesRef = ref(props.cues);
const currentTimeRef = ref(props.currentTime);

watch(() => props.cues, (v) => { cuesRef.value = v; });
watch(() => props.currentTime, (v) => { currentTimeRef.value = v; });

const { activeCueIndex } = useTranscript(cuesRef, currentTimeRef);

const listEl = ref<HTMLElement | null>(null);

// Auto-scroll: keep active cue visible without fighting user scroll
watch(activeCueIndex, async (idx) => {
  if (idx < 0 || !listEl.value) return;
  await nextTick();
  const item = listEl.value.children[idx] as HTMLElement | undefined;
  item?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
});

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}
</script>

<template>
  <div class="transcript-footer">
    <div v-if="cues.length === 0" class="transcript-empty">
      <span>Chưa có phụ đề. Chạy Transcription để tạo phụ đề.</span>
    </div>

    <div v-else ref="listEl" class="cue-list">
      <button
        v-for="(cue, idx) in cues"
        :key="cue.id"
        class="cue-item"
        :class="{ 'cue-item--active': activeCueIndex === idx }"
        @click="emit('seek', cue.start)"
      >
        <span class="cue-time">{{ formatTime(cue.start) }}</span>
        <span class="cue-texts">
          <span class="cue-original">{{ cue.originalText }}</span>
          <span class="cue-translated">{{ cue.translatedText }}</span>
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.transcript-footer {
  height: 160px;
  background: rgba(11, 15, 29, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.transcript-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #475569;
  font-size: 13px;
}

.cue-list {
  display: flex;
  gap: 0;
  overflow-x: auto;
  overflow-y: hidden;
  flex: 1;
  padding: 12px 16px;
  scroll-behavior: smooth;
  align-items: stretch;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.3) transparent;
}

.cue-list::-webkit-scrollbar { height: 4px; }
.cue-list::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.3);
  border-radius: 2px;
}

.cue-item {
  flex: 0 0 auto;
  min-width: 160px;
  max-width: 220px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 14px;
  margin-right: 8px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  text-align: left;
  transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
}

.cue-item:hover {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
}

.cue-item--active {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.25), 0 4px 16px rgba(99, 102, 241, 0.15);
  transform: translateY(-1px);
}

.cue-time {
  font-size: 10px;
  font-weight: 700;
  color: #6366f1;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.04em;
}

.cue-item--active .cue-time { color: #818cf8; }

.cue-texts {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cue-original {
  font-size: 12px;
  font-weight: 500;
  color: #e2e8f0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cue-translated {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cue-item--active .cue-original { color: #f1f5f9; }
.cue-item--active .cue-translated { color: #bae6fd; }
</style>
