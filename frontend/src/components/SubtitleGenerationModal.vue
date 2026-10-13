<script setup lang="ts">
import { computed, reactive } from 'vue';
import { SUPPORTED_LANGUAGES, SUPPORTED_SOURCE_LANGUAGES } from '../languages';
import type { PlaybackVideo, SubtitleJob } from '../types';
import { CheckCircle2, FileVideo, Sparkles, Subtitles, X, XCircle } from 'lucide-vue-next';

const props = defineProps<{ open: boolean; videos: PlaybackVideo[]; jobs: SubtitleJob[]; defaultTargetLanguage: string; activePath?: string }>();
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
function stateTone(video: PlaybackVideo): string {
  const job = latestJob(video);
  if (job?.status === 'waiting') return 'waiting';
  if (job?.status === 'processing') return 'processing';
  if (job?.status === 'failed') return 'failed';
  if (hasCache(video) || job?.status === 'completed') return 'cached';
  return 'ready';
}
const eligibleRequests = computed(() => props.videos.filter((video) => !hasCache(video) && !activeJob(video)).map((video) => ({ video, ...pairFor(video), force: false })));
</script>

<template>
  <div v-if="open" class="modal-backdrop" @click.self="emit('close')">
    <section class="generation-modal" role="dialog" aria-modal="true" aria-label="Tạo phụ đề">
      <header class="modal-header">
        <div class="title-block">
          <span class="title-icon" aria-hidden="true"><Subtitles :size="18" :stroke-width="1.75" /></span>
          <div>
            <h2>Phụ đề</h2>
            <p>Chọn cặp ngôn ngữ cho từng Video. Job chạy nền sau khi đóng.</p>
          </div>
        </div>
        <div class="header-actions">
          <div class="modal-actions">
            <button :disabled="eligibleRequests.length === 0" @click="emit('generate-all', eligibleRequests)">
              <Sparkles :size="16" :stroke-width="2" aria-hidden="true" />
              Tạo tất cả
            </button>
          </div>
          <button class="close-button" aria-label="Đóng modal phụ đề" @click="emit('close')"><X :size="17" aria-hidden="true" /></button>
        </div>
      </header>

      <p v-if="videos.length === 0" class="empty">Playback Queue chưa có Video.</p>
      <ol v-else class="modal-list">
        <li v-for="video in videos" :key="video.path" class="modal-row" :class="{ active: video.path === activePath }">
          <div class="row-head">
            <span class="row-icon" aria-hidden="true"><FileVideo :size="16" :stroke-width="1.75" /></span>
            <strong>{{ video.filename }}</strong>
            <span class="job-state" :class="stateTone(video)">
              <CheckCircle2 v-if="stateTone(video) === 'cached'" :size="13" aria-hidden="true" />
              <XCircle v-else-if="stateTone(video) === 'failed'" :size="13" aria-hidden="true" />
              <span v-else class="state-dot" aria-hidden="true"></span>
              {{ stateLabel(video) }}
            </span>
          </div>

          <div class="row-controls">
            <div class="language-pair">
              <label>Nguồn <select data-test="source-language" :value="pairFor(video).source" @change="setLanguage(video, 'source', $event)"><option v-for="language in SUPPORTED_SOURCE_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option></select></label>
              <label>Đích <select data-test="target-language" :value="pairFor(video).target" @change="setLanguage(video, 'target', $event)"><option v-for="language in SUPPORTED_LANGUAGES" :key="language.code" :value="language.code">{{ language.name }}</option></select></label>
            </div>
            <div class="row-actions">
              <button data-test="generate-video" :disabled="Boolean(activeJob(video))" @click="emit('generate', video, pairFor(video).source, pairFor(video).target, hasCache(video))">{{ hasCache(video) ? 'Tạo lại' : 'Tạo phụ đề' }}</button>
              <button v-if="latestJob(video)?.status === 'failed'" data-test="retry-job" @click="emit('retry', latestJob(video)!.id)">Thử lại</button>
            </div>
          </div>

          <span class="availability" :class="{ 'has-cache': video.cachedPairs?.length }">{{ video.cachedPairs?.length ? `Subtitle Availability: ${video.cachedPairs.map(([source, target]) => `${source} → ${target}`).join(', ')}` : 'Chưa có phụ đề' }}</span>
          <div v-if="latestJob(video)?.status === 'processing'" class="row-progress" aria-hidden="true">
            <span :style="{ width: `${Math.min(100, Math.max(0, latestJob(video)?.progress ?? 0))}%` }"></span>
          </div>
          <p v-if="latestJob(video)?.error" class="job-error">{{ latestJob(video)?.error }}</p>
        </li>
      </ol>
    </section>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 900;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  background: var(--bg-backdrop);
}

.generation-modal {
  width: min(var(--generation-width), 100%);
  max-height: min(var(--generation-height), 92vh);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--radius-panel);
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  color: var(--text-primary);
  box-shadow: var(--shadow-dropdown);
}

/* ── Header ─────────────────────────────────────────────────────────────── */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.title-block {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.title-icon {
  padding: 7px;
  box-sizing: content-box;
  border-radius: var(--radius-sm);
  background: var(--bg-raised);
  color: var(--text-secondary);
}

.modal-header h2 {
  margin: 0 0 2px;
  font-size: var(--font-title);
  font-weight: 600;
}

.modal-header p {
  margin: 0;
  color: var(--text-muted);
  font-size: var(--font-meta);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

/* ── Buttons ────────────────────────────────────────────────────────────── */
button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  min-height: var(--control-height);
  padding: 0 var(--space-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-control);
  background: var(--bg-raised);
  color: var(--text-primary);
  cursor: pointer;
  font-size: var(--font-meta);
  font-weight: 600;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

button:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-strong);
}

.modal-actions button {
  background: var(--accent);
  color: var(--accent-contrast);
  border-color: var(--accent);
  padding: 0 var(--space-4);
}

.modal-actions button:hover:not(:disabled) {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

.close-button {
  width: var(--control-height);
  padding: 0;
  background: transparent;
  border-color: transparent;
  color: var(--text-secondary);
}

.close-button:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* ── Rows ───────────────────────────────────────────────────────────────── */
.modal-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin: 0;
  padding: 0 var(--space-4);
  overflow-y: auto;
  list-style: none;
}

.modal-row {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3) 0;
  border-radius: 0;
  border: 0;
  border-bottom: 1px solid var(--border-subtle);
  background: transparent;
  transition: border-color var(--transition-fast), background-color var(--transition-fast);
}

.modal-row:hover {
  background: var(--bg-hover);
}

.modal-row.active {
  background: var(--accent-soft);
}

.row-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.row-icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.row-head strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--font-file);
  font-weight: 600;
}

.row-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.language-pair,
.row-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.language-pair label {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--text-muted);
  font-size: var(--font-meta);
  font-weight: 500;
}

.language-pair select {
  max-width: var(--source-select-width);
  min-height: var(--control-height);
  padding: 0 var(--space-2);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: var(--bg-field);
  color: var(--text-primary);
  font-size: var(--font-meta);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.language-pair select:focus-visible {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

/* ── State chip ─────────────────────────────────────────────────────────── */
.job-state {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-left: auto;
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.state-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.job-state.processing {
  color: var(--accent);
  border-color: color-mix(in srgb, var(--accent) 32%, transparent);
  background: var(--accent-soft);
}

.job-state.waiting {
  color: var(--warning);
  border-color: color-mix(in srgb, var(--warning) 32%, transparent);
  background: var(--warning-soft);
}

.job-state.cached {
  color: var(--success);
  border-color: color-mix(in srgb, var(--success) 32%, transparent);
  background: var(--success-soft);
}

.job-state.failed {
  color: var(--danger);
  border-color: color-mix(in srgb, var(--danger) 32%, transparent);
  background: var(--danger-soft);
}

/* ── Meta ───────────────────────────────────────────────────────────────── */
.availability,
.empty {
  font-size: var(--font-meta);
}

.availability,
.empty {
  color: var(--text-muted);
}

.availability.has-cache {
  color: var(--success);
}

.empty {
  padding: var(--space-8) var(--space-6);
  text-align: center;
}

.row-progress {
  height: 4px;
  border-radius: var(--radius-pill);
  overflow: hidden;
  background: var(--bg-active);
}

.row-progress span {
  display: block;
  height: 100%;
  border-radius: var(--radius-pill);
  background: var(--accent);
  transition: width var(--transition-base);
}

.job-error {
  margin: 0;
  color: var(--danger);
  font-size: var(--font-meta);
}
</style>
