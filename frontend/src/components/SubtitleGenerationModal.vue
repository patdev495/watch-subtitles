<script setup lang="ts">
import { computed, reactive } from 'vue';
import { SUPPORTED_LANGUAGES, SUPPORTED_SOURCE_LANGUAGES } from '../languages';
import type { PlaybackVideo, SubtitleJob } from '../types';

const props = defineProps<{ open: boolean; videos: PlaybackVideo[]; jobs: SubtitleJob[]; defaultTargetLanguage: string }>();
const emit = defineEmits<{
  (event: 'close'): void;
  (event: 'generate', video: PlaybackVideo, source: string, target: string, force: boolean): void;
  (event: 'generate-all', requests: { video: PlaybackVideo; source: string; target: string; force: boolean }[]): void;
  (event: 'retry', jobId: string): void;
  (event: 'source-change', video: PlaybackVideo, source: string): void;
}>();
const selection = reactive<Record<string, { source: string; target: string }>>({});
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
        <button aria-label="Đóng modal phụ đề" @click="emit('close')">×</button>
      </header>
      <div class="modal-actions"><button :disabled="eligibleRequests.length === 0" @click="emit('generate-all', eligibleRequests)">Tạo tất cả</button></div>
      <p v-if="videos.length === 0" class="empty">Playback Queue chưa có Video.</p>
      <ol v-else class="modal-list">
        <li v-for="video in videos" :key="video.path" class="modal-row">
          <strong>{{ video.filename }}</strong>
          <div class="language-pair">
            <label>Nguồn <select data-test="source-language" :value="pairFor(video).source" @change="setLanguage(video, 'source', $event)"><option v-for="language in SUPPORTED_SOURCE_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option></select></label>
            <label>Đích <select data-test="target-language" :value="pairFor(video).target" @change="setLanguage(video, 'target', $event)"><option v-for="language in SUPPORTED_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option></select></label>
          </div>
          <span class="availability">{{ video.cachedPairs?.length ? `Subtitle Availability: ${video.cachedPairs.map(([source, target]) => `${source} → ${target}`).join(', ')}` : 'Chưa có phụ đề' }}</span>
          <span class="job-state">{{ stateLabel(video) }}</span>
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
.modal-backdrop { position: fixed; inset: 0; z-index: 900; display: grid; place-items: center; padding: 18px; background: rgba(2, 6, 23, .78); }
.generation-modal { width: min(900px, 100%); max-height: min(760px, 92vh); overflow: auto; padding: 24px; border: 1px solid #475569; border-radius: 16px; color: #e2e8f0; background: #0f172a; box-shadow: 0 24px 70px #0009; }
.modal-header { display: flex; justify-content: space-between; gap: 16px; align-items: start; }.modal-header h2 { margin: 0 0 6px; }.modal-header p { margin: 0; color: #94a3b8; font-size: 13px; }
button { border: 1px solid #475569; border-radius: 8px; padding: 7px 12px; color: #e2e8f0; background: #1e293b; cursor: pointer; } button:disabled { opacity: .45; cursor: not-allowed; }
.modal-actions { display: flex; justify-content: flex-end; margin: 18px 0; }.modal-actions button, .row-actions button:first-child { background: #3730a3; }
.modal-list { display: grid; gap: 10px; padding: 0; margin: 0; list-style: none; }.modal-row { display: grid; gap: 9px; padding: 14px; border: 1px solid #334155; border-radius: 10px; background: #111c2f; }.modal-row strong { overflow-wrap: anywhere; }
.language-pair, .row-actions { display: flex; flex-wrap: wrap; gap: 10px; }.language-pair label { display: flex; align-items: center; gap: 6px; font-size: 12px; }.language-pair select { max-width: 180px; padding: 5px; color: #e2e8f0; background: #1e293b; border: 1px solid #475569; border-radius: 5px; }.availability, .job-state, .job-error, .empty { font-size: 12px; }.availability { color: #a5b4fc; }.job-state { color: #67e8f9; }.job-error { color: #fda4af; margin: 0; }
</style>
