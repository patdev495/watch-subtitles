<script setup lang="ts">
import { computed, reactive } from 'vue';
import { SUPPORTED_LANGUAGES, SUPPORTED_SOURCE_LANGUAGES } from '../languages';
import type { PlaybackVideo, SubtitleJob } from '../types';
import { X } from 'lucide-vue-next';

const props = defineProps<{ open: boolean; videos: PlaybackVideo[]; jobs: SubtitleJob[]; defaultTargetLanguage: string; activePath?: string }>();
const emit = defineEmits<{
  (event: 'close'): void;
  (event: 'generate', video: PlaybackVideo, source: string, target: string, force: boolean): void;
  (event: 'generate-all', requests: { video: PlaybackVideo; source: string; target: string; force: boolean }[]): void;
  (event: 'retry', jobId: string): void;
  (event: 'source-change', video: PlaybackVideo, source: string): void;
}>();
const selection = reactive<Record<string, { source: string; target: string }>>({});
const selectedVideo = computed(() => props.videos.find((video) => video.path === props.activePath) ?? props.videos[0]);
function pairFor(video: PlaybackVideo): { source: string; target: string } {
  return selection[video.path] ?? { source: video.sourceLanguage ?? 'en', target: props.defaultTargetLanguage };
}
function setLanguage(video: PlaybackVideo, kind: 'source' | 'target', event: Event): void {
  selection[video.path] = { ...pairFor(video), [kind]: (event.target as HTMLSelectElement).value };
  if (kind === 'source') emit('source-change', video, selection[video.path].source);
}
function hasCache(video: PlaybackVideo): boolean {
  const pair = pairFor(video);
  return video.cachedPairs?.some(([source, target]) => source === pair.source && target === pair.target) ?? false;
}
function matchingJobs(video: PlaybackVideo): SubtitleJob[] {
  const pair = pairFor(video);
  return props.jobs.filter((job) => job.video_path === video.path && job.source_language === pair.source && job.target_language === pair.target);
}
function activeJob(video: PlaybackVideo): SubtitleJob | undefined {
  return matchingJobs(video).find((job) => job.status === 'waiting' || job.status === 'processing');
}
function latestJob(video: PlaybackVideo): SubtitleJob | undefined { return matchingJobs(video).at(-1); }
function stateLabel(video: PlaybackVideo): string {
  const job = latestJob(video);
  if (job?.status === 'waiting') return 'Đang chờ';
  if (job?.status === 'processing') return `Đang xử lý · ${Math.round(job.progress)}%`;
  if (job?.status === 'failed') return 'Thất bại';
  if (hasCache(video) || job?.status === 'completed') return 'Đã có Subtitle Cache';
  return 'Sẵn sàng tạo';
}
const eligibleRequests = computed(() => props.videos.filter((video) => !hasCache(video) && !activeJob(video)).map((video) => ({ video, ...pairFor(video), force: false })));
</script>

<template>
  <div v-if="open" class="modal-backdrop" @click.self="emit('close')">
    <section class="generation-modal" role="dialog" aria-modal="true" aria-label="Tạo phụ đề">
      <header class="modal-header">
        <div><h2>Phụ đề</h2><p>Chọn cặp ngôn ngữ cho từng Video. Job chạy nền sau khi đóng.</p></div>
        <button class="close-button" aria-label="Đóng modal phụ đề" @click="emit('close')"><X :size="16" aria-hidden="true" /></button>
      </header>
      <div class="modal-actions"><button :disabled="eligibleRequests.length === 0" @click="emit('generate-all', eligibleRequests)">Tạo tất cả</button></div>
      <div v-if="selectedVideo" class="active-language-pair">
        <strong :title="selectedVideo.filename">{{ selectedVideo.filename }}</strong>
        <div class="language-pair">
          <label>Nguồn <select data-test="source-language" :value="pairFor(selectedVideo).source" @change="setLanguage(selectedVideo, 'source', $event)"><option v-for="language in SUPPORTED_SOURCE_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option></select></label>
          <label>Đích <select data-test="target-language" :value="pairFor(selectedVideo).target" @change="setLanguage(selectedVideo, 'target', $event)"><option v-for="language in SUPPORTED_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option></select></label>
        </div>
      </div>
      <p v-if="videos.length === 0" class="empty">Playback Queue chưa có Video.</p>
      <ol v-else class="modal-list">
        <li v-for="video in videos" :key="video.path" class="modal-row">
          <strong>{{ video.filename }}</strong>
          <span class="availability" :class="{ 'has-cache': video.cachedPairs?.length }">{{ video.cachedPairs?.length ? `Subtitle Availability: ${video.cachedPairs.map(([source, target]) => `${source} → ${target}`).join(', ')}` : 'Chưa có phụ đề' }}</span>
          <span class="job-state" :class="{ 'in-progress': activeJob(video), failed: latestJob(video)?.status === 'failed' }">{{ stateLabel(video) }}</span>
          <p v-if="latestJob(video)?.error" class="job-error">{{ latestJob(video)?.error }}</p>
          <div class="row-actions">
            <button data-test="generate-video" :disabled="Boolean(activeJob(video))" @click="emit('generate', video, pairFor(video).source, pairFor(video).target, hasCache(video))">{{ hasCache(video) ? 'Tạo lại' : 'Tạo phụ đề' }}</button>
            <button v-if="latestJob(video)?.status === 'failed'" data-test="retry-job" @click="emit('retry', latestJob(video)!.id)">Thử lại</button>
          </div>
        </li>
      </ol>
    </section>
  </div>
</template>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; z-index: 900; display: grid; place-items: center; padding: var(--space-4); background: var(--bg-backdrop); }
.generation-modal { width: min(var(--generation-width), 100%); max-height: min(var(--generation-height), 92vh); overflow: auto; padding: var(--space-6); border-radius: var(--radius-card); background: var(--bg-surface); color: var(--text-primary); box-shadow: var(--shadow-panel); }
.modal-header { display: flex; justify-content: space-between; align-items: start; gap: var(--space-4); }
.modal-header h2 { margin: 0 0 var(--space-1); font-size: var(--font-title); font-weight: 600; }
.modal-header p { margin: 0; color: var(--text-secondary); font-size: var(--font-body); }
button { display: inline-flex; align-items: center; justify-content: center; min-height: var(--control-height); padding: 0 var(--space-3); border: 0; border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-primary); cursor: pointer; font-size: var(--font-meta); font-weight: 500; }
button:hover:not(:disabled) { background: var(--bg-selected); }
.close-button { width: var(--control-height); padding: 0; background: transparent; }
.modal-actions { display: flex; justify-content: flex-end; margin: var(--space-4) 0; }
.modal-actions button { background: var(--accent-primary); color: var(--accent-contrast); }
.modal-actions button:hover:not(:disabled) { opacity: .88; background: var(--accent-primary); }
.active-language-pair { display: grid; gap: var(--space-2); margin-bottom: var(--space-4); padding: var(--space-3); border-radius: var(--radius-control); background: var(--bg-hover); }
.active-language-pair strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: var(--font-file); font-weight: 500; }
.modal-list { display: grid; gap: var(--space-1); margin: 0; padding: 0; list-style: none; }
.modal-row { display: grid; gap: var(--space-2); padding: var(--space-3); border-radius: var(--radius-control); }
.modal-row:hover { background: var(--bg-hover); }
.modal-row strong { overflow-wrap: anywhere; font-size: var(--font-file); font-weight: 500; }
.language-pair, .row-actions { display: flex; flex-wrap: wrap; gap: var(--space-2); }
.language-pair label { display: flex; align-items: center; gap: var(--space-1); color: var(--text-secondary); font-size: var(--font-meta); }
.language-pair select { max-width: var(--source-select-width); min-height: var(--control-height); padding: 0 var(--space-2); border: 1px solid var(--border-subtle); border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-primary); }
.availability, .job-state, .job-error, .empty { font-size: var(--font-meta); }
.availability, .empty { color: var(--text-muted); }
.availability.has-cache, .job-state, .job-state.in-progress { color: var(--text-secondary); }
.job-state.failed, .job-error { color: var(--text-primary); }
.job-error { margin: 0; }
</style>
