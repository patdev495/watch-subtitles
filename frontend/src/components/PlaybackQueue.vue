<script setup lang="ts">
import type { PlaybackVideo, SubtitleJob } from '../types';
import { SUPPORTED_SOURCE_LANGUAGES } from '../languages';

defineProps<{
  videos: PlaybackVideo[];
  jobs: SubtitleJob[];
  activePath: string;
  autoAdvance: boolean;
}>();
const emit = defineEmits<{
  (event: 'select', video: PlaybackVideo): void;
  (event: 'remove', video: PlaybackVideo): void;
  (event: 'clear'): void;
  (event: 'add-files'): void;
  (event: 'add-folder'): void;
  (event: 'update:autoAdvance', enabled: boolean): void;
  (event: 'source-change', video: PlaybackVideo, source: string): void;
}>();

function currentJob(jobs: SubtitleJob[], path: string): SubtitleJob | undefined {
  return jobs.filter((job) => job.video_path === path && ['waiting', 'processing'].includes(job.status)).at(-1);
}
</script>

<template>
  <aside class="playback-queue" aria-label="Playback Queue">
    <header>
      <h2>Hàng đợi phát</h2>
      <div class="queue-imports">
        <button @click="emit('add-files')">Thêm video</button>
        <button @click="emit('add-folder')">Thêm thư mục</button>
      </div>
      <button class="clear-queue" aria-label="Xóa tất cả video khỏi hàng đợi phát" :disabled="videos.length === 0" @click="emit('clear')">Xóa tất cả</button>
      <label class="auto-advance"><input type="checkbox" :checked="autoAdvance" @change="emit('update:autoAdvance', ($event.target as HTMLInputElement).checked)" /> Tự chuyển video</label>
    </header>
    <p v-if="videos.length === 0" class="empty">Chưa có video.</p>
    <ol v-else>
      <li v-for="video in videos" :key="video.path" :data-test="video.path === activePath ? 'queue-row-active' : 'queue-row'" :class="{ active: video.path === activePath }">
        <button class="queue-select" :data-test="`queue-select-${video.filename.charAt(0)}`" @click="emit('select', video)">{{ video.filename }}</button>
        <button class="queue-remove" :data-test="`queue-remove-${video.filename.charAt(0)}`" :aria-label="`Xóa ${video.filename}`" @click="emit('remove', video)">×</button>
        <label class="source">Nguồn
          <select :value="video.sourceLanguage" @change="emit('source-change', video, ($event.target as HTMLSelectElement).value)">
            <option v-for="language in SUPPORTED_SOURCE_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option>
          </select>
        </label>
        <span class="availability">{{ video.cachedPairs?.length ? video.cachedPairs.map(([source, target]) => `${source} → ${target}`).join(', ') : 'Chưa có phụ đề' }}</span>
        <span v-if="currentJob(jobs, video.path)" class="progress">{{ currentJob(jobs, video.path)?.status === 'processing' ? `${currentJob(jobs, video.path)?.progress}%` : 'Đang chờ' }}</span>
        <span v-if="video.error" class="error">{{ video.error }}</span>
      </li>
    </ol>
  </aside>
</template>

<style scoped>
.playback-queue { width: 320px; flex: 0 0 320px; min-height: 0; overflow-y: auto; padding: 18px 12px; border-right: 1px solid rgba(148,163,184,.18); color: #e2e8f0; background: #0b1220; }
h2 { margin: 0 0 14px; font-size: 16px; }
.queue-imports { display: flex; gap: 6px; }
button { cursor: pointer; color: inherit; background: #1e293b; border: 1px solid #334155; border-radius: 7px; padding: 7px; }
button:disabled { opacity: .45; cursor: not-allowed; }.clear-queue { margin-top: 8px; color: #fda4af; border-color: #7f1d1d; }.clear-queue:hover:not(:disabled) { background: #450a0a; }
.auto-advance { display: flex; align-items: center; gap: 6px; margin: 14px 0; font-size: 13px; }
.empty { color: #94a3b8; font-size: 13px; }
ol { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
li { display: grid; grid-template-columns: 1fr auto; gap: 5px; padding: 10px; border: 1px solid #334155; border-radius: 10px; background: #111c2f; }
li.active { border-color: #818cf8; background: #202547; }
.queue-select { text-align: left; overflow-wrap: anywhere; font-weight: 700; background: none; border: 0; }
.queue-remove { line-height: 1; color: #fda4af; }
.source { grid-column: 1 / -1; font-size: 11px; color: #94a3b8; }
.source select { margin-left: 5px; max-width: 160px; color: #e2e8f0; background: #1e293b; border: 1px solid #475569; }
.availability,.progress,.error { grid-column: 1 / -1; font-size: 11px; }
.availability { color: #a5b4fc; }.progress { color: #67e8f9; }.error { color: #fda4af; }
@media (max-width: 700px) { .playback-queue { width: 180px; flex-basis: 180px; } .queue-imports { flex-direction: column; } }
</style>
