<script setup lang="ts">
import type { PlaybackVideo, SubtitleJob } from '../types';
import { FolderPlus, ListPlus, Trash2, X } from 'lucide-vue-next';

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
  <aside class="playback-queue" aria-label="Thư viện video">
    <header class="queue-header">
      <div class="queue-heading"><h2>Thư viện</h2><span>{{ videos.length }}</span></div>
      <div class="queue-actions">
        <button aria-label="Thêm video" title="Thêm video" @click="emit('add-files')"><ListPlus :size="16" :stroke-width="1.5" aria-hidden="true" /></button>
        <button aria-label="Thêm thư mục" title="Thêm thư mục" @click="emit('add-folder')"><FolderPlus :size="16" :stroke-width="1.5" aria-hidden="true" /></button>
        <button class="clear-queue" aria-label="Xóa tất cả video khỏi hàng đợi phát" title="Xóa tất cả" :disabled="videos.length === 0" @click="emit('clear')"><Trash2 :size="16" :stroke-width="1.5" aria-hidden="true" /></button>
      </div>
      <label class="auto-advance"><input type="checkbox" :checked="autoAdvance" @change="emit('update:autoAdvance', ($event.target as HTMLInputElement).checked)" /> Tự chuyển video</label>
    </header>
    <p v-if="videos.length === 0" class="empty">Chưa có video.</p>
    <ol v-else class="video-list">
      <li v-for="video in videos" :key="video.path" :data-test="video.path === activePath ? 'queue-row-active' : 'queue-row'" :class="{ active: video.path === activePath }">
        <button class="queue-select" :data-test="`queue-select-${video.filename.charAt(0)}`" :title="video.filename" @click="emit('select', video)">
          <span class="filename">{{ video.filename }}</span>
          <span class="row-meta">
            <template v-if="video.cachedPairs?.length"><span v-for="([source, target], index) in video.cachedPairs" :key="`${source}-${target}-${index}`" class="language-badge">{{ source.toUpperCase() }}→{{ target.toUpperCase() }}</span></template>
            <span v-else class="no-subtitles">Chưa có phụ đề</span>
          </span>
        </button>
        <button class="queue-remove" :data-test="`queue-remove-${video.filename.charAt(0)}`" :aria-label="`Xóa ${video.filename}`" :title="`Xóa ${video.filename}`" @click="emit('remove', video)"><X :size="16" :stroke-width="1.5" aria-hidden="true" /></button>
        <span v-if="currentJob(jobs, video.path)" class="job-indicator" :title="currentJob(jobs, video.path)?.status === 'processing' ? `${currentJob(jobs, video.path)?.progress}%` : 'Đang chờ'" aria-label="Đang tạo phụ đề"></span>
        <span v-if="video.error" class="row-error" :title="video.error" aria-label="Lỗi video">!</span>
      </li>
    </ol>
  </aside>
</template>

<style scoped>
.playback-queue { width: var(--sidebar-width); flex: 0 0 var(--sidebar-width); min-height: 0; overflow-y: auto; border-right: 1px solid var(--border-subtle); background: var(--bg-surface); color: var(--text-primary); }
.queue-header { display: grid; grid-template-columns: 1fr auto; align-items: center; gap: var(--space-2); padding: var(--space-4) var(--space-3) var(--space-3); }
.queue-heading { display: flex; align-items: center; gap: var(--space-2); min-width: 0; }
h2 { margin: 0; font-size: var(--font-meta); font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--text-muted); }
.queue-heading span { color: var(--text-muted); font-size: var(--font-meta); }
.queue-actions { display: flex; gap: var(--space-1); }
.queue-actions button { width: var(--control-height); height: var(--control-height); display: grid; place-items: center; padding: 0; border: 0; border-radius: var(--radius-control); background: transparent; color: var(--text-secondary); cursor: pointer; }
.queue-actions button:hover:not(:disabled) { background: var(--bg-hover); color: var(--text-primary); }
.queue-actions .clear-queue:hover:not(:disabled) { color: var(--danger); }
.auto-advance { grid-column: 1 / -1; display: flex; align-items: center; gap: var(--space-2); color: var(--text-secondary); font-size: var(--font-meta); cursor: pointer; }
.auto-advance input { margin: 0; }
.empty { margin: var(--space-3); color: var(--text-muted); font-size: var(--font-meta); }
.video-list { list-style: none; margin: 0; padding: 0 var(--space-2) var(--space-3); display: grid; gap: var(--row-gap); }
li { position: relative; min-height: var(--row-height); display: flex; align-items: center; border-radius: var(--radius-control); background: transparent; }
li:hover { background: var(--bg-hover); }
li.active { background: var(--bg-selected); }
li.active::before { content: ''; position: absolute; top: var(--space-2); bottom: var(--space-2); left: 0; width: var(--indicator-width); border-radius: var(--radius-sm); background: var(--accent-primary); }
.queue-select { min-width: 0; width: 100%; min-height: var(--row-height); display: grid; align-content: center; gap: var(--space-1); padding: var(--space-2) var(--space-3); border: 0; background: transparent; color: var(--text-primary); text-align: left; cursor: pointer; }
.filename { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: var(--font-file); font-weight: 500; line-height: 1.2; }
.row-meta { min-width: 0; display: flex; align-items: center; gap: var(--space-1); overflow: hidden; white-space: nowrap; }
.language-badge { padding: 0 var(--space-1); border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-secondary); font-size: var(--font-meta); line-height: 1.5; }
.no-subtitles { color: var(--text-muted); font-size: var(--font-meta); }
.queue-remove { position: absolute; top: var(--space-2); right: var(--space-2); width: var(--control-height); height: var(--control-height); display: grid; place-items: center; padding: 0; border: 0; border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-secondary); opacity: 0; cursor: pointer; }
li:hover .queue-remove, li:focus-within .queue-remove { opacity: 1; }
.queue-remove:hover { color: var(--danger); }
.job-indicator { position: absolute; right: var(--space-3); bottom: var(--space-2); width: var(--space-2); height: var(--space-2); border: 1px solid var(--text-secondary); border-top-color: transparent; border-radius: 50%; animation: spin .8s linear infinite; }
.row-error { position: absolute; right: var(--space-3); bottom: var(--space-2); color: var(--text-secondary); font-size: var(--font-meta); }
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .job-indicator { animation: none; } }
</style>
