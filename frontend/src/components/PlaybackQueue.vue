<script setup lang="ts">
import type { PlaybackVideo, SubtitleJob } from '../types';
import { SUPPORTED_SOURCE_LANGUAGES } from '../languages';
import { X } from 'lucide-vue-next';

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
        <button class="queue-remove" :data-test="`queue-remove-${video.filename.charAt(0)}`" :aria-label="`Xóa ${video.filename}`" @click="emit('remove', video)"><X :size="15" aria-hidden="true" /></button>
        <label class="source">Nguồn
          <select :value="video.sourceLanguage" @change="emit('source-change', video, ($event.target as HTMLSelectElement).value)">
            <option v-for="language in SUPPORTED_SOURCE_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option>
          </select>
        </label>
        <span class="availability" :class="{ 'has-cache': video.cachedPairs?.length }">{{ video.cachedPairs?.length ? video.cachedPairs.map(([source, target]) => `${source} → ${target}`).join(', ') : 'Chưa có phụ đề' }}</span>
        <span v-if="currentJob(jobs, video.path)" class="progress">{{ currentJob(jobs, video.path)?.status === 'processing' ? `${currentJob(jobs, video.path)?.progress}%` : 'Đang chờ' }}</span>
        <span v-if="video.error" class="error">{{ video.error }}</span>
      </li>
    </ol>
  </aside>
</template>

<style scoped>
.playback-queue { width: 320px; flex: 0 0 320px; min-height: 0; overflow-y: auto; padding: 18px 12px; border-right: 1px solid var(--border-subtle); color: var(--text-primary); background: var(--bg-surface); }
h2 { margin: 0 0 14px; font-size: 15px; font-weight: 700; letter-spacing: -.02em; }
.queue-imports { display: flex; gap: 6px; }
button { min-height: var(--control-height); padding: 0 10px; cursor: pointer; color: var(--text-secondary); background: var(--bg-control); border: 1px solid var(--border-subtle); border-radius: var(--radius-control); font-size: 12px; font-weight: 600; }
button:hover:not(:disabled) { color: var(--text-primary); background: var(--bg-raised); border-color: var(--border-strong); }
.clear-queue { margin-top: 8px; color: var(--text-muted); background: transparent; }
.clear-queue:hover:not(:disabled) { color: var(--danger); border-color: var(--danger); }
.auto-advance { display: flex; align-items: center; gap: 6px; margin: 14px 0; font-size: 12px; color: var(--text-secondary); }
.auto-advance input { margin: 0; }
.empty { color: var(--text-muted); font-size: 12px; }
ol { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
li { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 5px; padding: 10px; border: 1px solid var(--border-subtle); border-radius: var(--radius-control); background: var(--bg-card); }
li.active { border-color: var(--accent-primary); background: var(--accent-soft); }
.queue-select { min-width: 0; min-height: 26px; padding: 0; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; color: var(--text-primary); background: none; border: 0; }
.queue-select:hover:not(:disabled) { background: none; border-color: transparent; color: var(--accent-hover); }
.queue-remove { display: grid; place-items: center; width: 26px; height: 26px; min-height: 26px; padding: 0; line-height: 1; color: var(--text-muted); background: transparent; border: 0; }
.queue-remove:hover:not(:disabled) { color: var(--danger); background: var(--bg-raised); border-color: transparent; }
.source { grid-column: 1 / -1; font-size: 11px; color: var(--text-muted); }
.source select { margin-left: 5px; max-width: 160px; min-height: 27px; padding: 2px 6px; color: var(--text-secondary); background: var(--bg-control); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); }
.availability,.progress,.error { grid-column: 1 / -1; font-size: 11px; }
.availability { color: var(--text-muted); }.availability.has-cache { color: var(--success); }.progress { color: var(--warning); }.error { color: var(--danger); }
@media (max-width: 700px) { .playback-queue { width: 180px; flex-basis: 180px; } .queue-imports { flex-direction: column; } }
</style>
