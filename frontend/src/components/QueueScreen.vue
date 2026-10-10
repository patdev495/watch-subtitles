<script setup lang="ts">
import { computed, reactive } from 'vue';
import { ArrowLeft, CheckCircle2, Clock3, Film, Languages, LoaderCircle, Play, Plus, RotateCcw, Sparkles, Trash2, XCircle } from 'lucide-vue-next';
import { SUPPORTED_LANGUAGES, SUPPORTED_SOURCE_LANGUAGES } from '../languages';
import type { SubtitleJob } from '../types';

export interface QueuedVideo { path: string; filename: string; cachedPairs?: [string, string][]; }
export interface QueueGenerationRequest { video: QueuedVideo; source: string; target: string; force: boolean; }

const props = defineProps<{ videos: QueuedVideo[]; jobs: SubtitleJob[]; sourceLanguage: string; targetLanguage: string; }>();
const emit = defineEmits<{
  (event: 'add'): void;
  (event: 'generate', video: QueuedVideo, source: string, target: string, force: boolean): void;
  (event: 'generate-all', requests: QueueGenerationRequest[]): void;
  (event: 'play', video: QueuedVideo, source: string, target: string): void;
  (event: 'remove-video', video: QueuedVideo): void;
  (event: 'retry', jobId: string): void;
  (event: 'remove-job', jobId: string): void;
  (event: 'back'): void;
}>();

const activeJobs = computed(() => props.jobs.filter((job) => ['waiting', 'processing'].includes(job.status)).length);
const completedJobs = computed(() => props.jobs.filter((job) => job.status === 'completed').length);
const selection = reactive<Record<string, { source: string; target: string }>>({});
const sourceLanguages = SUPPORTED_SOURCE_LANGUAGES;
const targetLanguages = SUPPORTED_LANGUAGES;
function jobsFor(video: QueuedVideo): SubtitleJob[] { return props.jobs.filter((job) => job.video_path === video.path); }
function latestJob(video: QueuedVideo): SubtitleJob | undefined { return jobsFor(video).at(-1); }
function pairFor(video: QueuedVideo): { source: string; target: string } { return selection[video.path] ?? { source: props.sourceLanguage, target: props.targetLanguage }; }
function setLanguage(video: QueuedVideo, kind: 'source' | 'target', event: Event): void {
  selection[video.path] = { ...pairFor(video), [kind]: (event.target as HTMLSelectElement).value };
}
function hasCache(video: QueuedVideo): boolean { const pair = pairFor(video); return video.cachedPairs?.some(([source, target]) => source === pair.source && target === pair.target) ?? false; }
function stateLabel(job?: SubtitleJob): string {
  if (!job) return 'Sẵn sàng tạo';
  return { waiting: 'Đang chờ', processing: 'Đang xử lý', completed: job.cached ? 'Từ Subtitle Cache' : 'Hoàn tất', failed: 'Thất bại', cancelled: 'Đã hủy' }[job.status];
}
</script>

<template>
  <section class="queue-screen" aria-label="Subtitle Queue">
    <header class="queue-header">
      <div class="queue-heading">
        <p class="eyebrow"><Sparkles :size="14" aria-hidden="true" /> SUBTITLE QUEUE</p>
        <h2>Hàng đợi tạo phụ đề</h2>
        <p>Video đang phát vẫn giữ nguyên. Các job chạy lần lượt theo thứ tự bên dưới.</p>
      </div>
      <div class="queue-actions">
        <button class="quiet-button" @click="emit('back')"><ArrowLeft :size="17" aria-hidden="true" /> Trình phát</button>
        <button class="secondary-button" @click="emit('add')"><Plus :size="17" aria-hidden="true" /> Thêm video</button>
        <button class="primary-button" :disabled="videos.length === 0" @click="emit('generate-all', videos.map((video) => ({ video, ...pairFor(video), force: hasCache(video) })))"><Sparkles :size="17" aria-hidden="true" /> Tạo tất cả</button>
      </div>
    </header>

    <div class="stats" aria-label="Tổng quan hàng đợi">
      <div class="stat"><Film :size="18" aria-hidden="true" /><span><strong>{{ videos.length }}</strong> video trong hàng đợi</span></div>
      <div class="stat"><LoaderCircle :size="18" aria-hidden="true" /><span><strong>{{ activeJobs }}</strong> job đang chờ/xử lý</span></div>
      <div class="stat"><CheckCircle2 :size="18" aria-hidden="true" /><span><strong>{{ completedJobs }}</strong> job hoàn tất</span></div>
    </div>

    <div v-if="videos.length === 0" class="empty">
      <div class="empty-icon"><Film :size="28" aria-hidden="true" /></div>
      <h3>Hàng đợi đang trống</h3>
      <p>Thêm video để chuẩn bị tạo phụ đề mà không đổi video đang phát.</p>
      <button class="primary-button" @click="emit('add')"><Plus :size="17" aria-hidden="true" /> Thêm video đầu tiên</button>
    </div>

    <ol v-else class="queue-list">
      <li v-for="(video, index) in videos" :key="video.path" class="video-card">
        <div class="queue-number" :aria-label="`Thứ tự ${index + 1}`">#{{ index + 1 }}</div>
        <div class="video-icon"><Film :size="20" aria-hidden="true" /></div>
        <div class="video-copy">
          <strong :title="video.filename">{{ video.filename }}</strong>
          <div class="video-meta">
            <span class="language-pair"><Languages :size="14" aria-hidden="true" />
              <label class="sr-only" :for="`source-${index}`">Ngôn ngữ nguồn</label><select :id="`source-${index}`" data-test="source-language" :value="pairFor(video).source" @change="setLanguage(video, 'source', $event)"><option v-for="language in sourceLanguages" :key="language.code" :value="language.code">{{ language.name }}</option></select>
              <span aria-hidden="true">→</span>
              <label class="sr-only" :for="`target-${index}`">Ngôn ngữ đích</label><select :id="`target-${index}`" data-test="target-language" :value="pairFor(video).target" @change="setLanguage(video, 'target', $event)"><option v-for="language in targetLanguages" :key="language.code" :value="language.code">{{ language.name }}</option></select>
            </span>
            <span v-if="latestJob(video)" :class="['state-pill', latestJob(video)?.status]">
              <LoaderCircle v-if="latestJob(video)?.status === 'processing'" :size="13" aria-hidden="true" />
              <Clock3 v-else-if="latestJob(video)?.status === 'waiting'" :size="13" aria-hidden="true" />
              <CheckCircle2 v-else-if="latestJob(video)?.status === 'completed'" :size="13" aria-hidden="true" />
              <XCircle v-else :size="13" aria-hidden="true" />
              {{ stateLabel(latestJob(video)) }}<template v-if="latestJob(video)?.status === 'processing'"> · {{ latestJob(video)?.progress }}%</template>
            </span>
            <span v-else class="state-pill idle">{{ stateLabel() }}</span>
          </div>
          <p v-if="latestJob(video)?.error" class="job-error">{{ latestJob(video)?.error }}</p>
          <p v-else-if="jobsFor(video).length > 1" class="job-history">{{ jobsFor(video).map((job) => `${job.source_language}→${job.target_language}`).join('  ·  ') }}</p>
        </div>
        <div class="video-actions">
          <button data-test="play-video" class="secondary-button" @click="emit('play', video, pairFor(video).source, pairFor(video).target)"><Play :size="16" aria-hidden="true" /> Xem</button>
          <button v-if="latestJob(video)?.status === 'failed'" data-test="retry-job" class="secondary-button" @click="emit('retry', latestJob(video)?.id ?? '')"><RotateCcw :size="16" aria-hidden="true" /> Thử lại</button>
          <button v-else data-test="generate-video" class="primary-button" :disabled="['waiting', 'processing'].includes(latestJob(video)?.status ?? '')" @click="emit('generate', video, pairFor(video).source, pairFor(video).target, hasCache(video))"><Sparkles :size="16" aria-hidden="true" /> {{ hasCache(video) ? 'Tạo lại phụ đề' : 'Tạo phụ đề' }}</button>
          <button v-if="latestJob(video)?.status === 'waiting'" data-test="remove-job" class="icon-button" title="Xóa job đang chờ" aria-label="Xóa job đang chờ" @click="emit('remove-job', latestJob(video)?.id ?? '')"><XCircle :size="17" aria-hidden="true" /></button>
          <button class="icon-button danger" :disabled="latestJob(video)?.status === 'processing'" title="Xóa video khỏi hàng đợi" aria-label="Xóa video khỏi hàng đợi" @click="emit('remove-video', video)"><Trash2 :size="17" aria-hidden="true" /></button>
        </div>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.queue-screen { flex: 1; overflow: auto; padding: 34px clamp(24px, 4vw, 64px) 56px; color: var(--text-primary); background: radial-gradient(circle at 84% 4%, rgba(49, 46, 129, .22), transparent 30%); }.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; }
.queue-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; margin: 0 auto 24px; max-width: 1280px; }.queue-heading h2 { margin: 7px 0 8px; font-size: clamp(26px, 3vw, 36px); letter-spacing: -.04em; }.queue-heading > p:last-child { margin: 0; color: var(--text-secondary); font-size: 15px; }.eyebrow { display: flex; align-items: center; gap: 6px; margin: 0; color: #a5b4fc; font-size: 11px; font-weight: 800; letter-spacing: .13em; }.queue-actions, .video-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
button { display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-height: 38px; border: 1px solid transparent; border-radius: 9px; padding: 0 13px; font: inherit; font-size: 13px; font-weight: 750; cursor: pointer; transition: background .18s ease, border-color .18s ease, transform .18s ease; } button:hover:not(:disabled) { transform: translateY(-1px); } button:disabled { cursor: not-allowed; opacity: .45; }.primary-button { color: #fff; background: linear-gradient(135deg, #6366f1, #2563eb); box-shadow: 0 8px 20px rgba(37, 99, 235, .23); }.secondary-button, .quiet-button, .icon-button { color: #dbeafe; background: rgba(30, 41, 59, .72); border-color: rgba(148, 163, 184, .18); }.quiet-button { color: #94a3b8; background: transparent; }.icon-button { min-width: 38px; padding: 0; }.icon-button.danger { color: #fda4af; }.icon-button.danger:hover:not(:disabled) { background: rgba(127, 29, 29, .45); border-color: rgba(251, 113, 133, .45); }
.stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; max-width: 1280px; margin: 0 auto 18px; }.stat { display: flex; align-items: center; gap: 10px; padding: 13px 16px; border: 1px solid rgba(148, 163, 184, .14); border-radius: 12px; color: #94a3b8; background: rgba(15, 23, 42, .56); font-size: 12px; }.stat svg { color: #818cf8; }.stat strong { color: #e2e8f0; font-size: 16px; }
.queue-list { display: grid; gap: 10px; max-width: 1280px; margin: 0 auto; padding: 0; list-style: none; }.video-card { display: grid; grid-template-columns: auto auto minmax(0, 1fr) auto; align-items: center; gap: 14px; padding: 16px 18px; border: 1px solid rgba(148, 163, 184, .16); border-radius: 14px; background: linear-gradient(100deg, rgba(15, 23, 42, .86), rgba(15, 23, 42, .58)); box-shadow: 0 12px 30px rgba(0, 0, 0, .14); }.video-card:hover { border-color: rgba(129, 140, 248, .42); }.queue-number { min-width: 30px; color: #818cf8; font: 750 13px var(--font-mono); }.video-icon, .empty-icon { display: grid; place-items: center; color: #93c5fd; background: rgba(59, 130, 246, .12); border: 1px solid rgba(96, 165, 250, .22); border-radius: 10px; }.video-icon { width: 40px; height: 40px; }.video-copy { min-width: 0; }.video-copy strong { display: block; overflow: hidden; color: #f8fafc; font-size: 15px; text-overflow: ellipsis; white-space: nowrap; }.video-meta { display: flex; align-items: center; gap: 8px; margin-top: 7px; flex-wrap: wrap; }.language-pair, .state-pill { display: inline-flex; align-items: center; gap: 5px; border-radius: 999px; padding: 4px 8px; font-size: 11px; font-weight: 700; }.language-pair { color: #bfdbfe; background: rgba(30, 64, 175, .22); }.language-pair select { max-width: 105px; border: 0; color: inherit; background: transparent; font: inherit; outline: none; cursor: pointer; }.language-pair select option { color: #e2e8f0; background: #172033; }.state-pill { color: #cbd5e1; background: rgba(71, 85, 105, .42); }.state-pill.processing { color: #7dd3fc; background: rgba(14, 116, 144, .25); }.state-pill.processing svg { animation: spin 1s linear infinite; }.state-pill.completed { color: #86efac; background: rgba(6, 95, 70, .3); }.state-pill.failed { color: #fda4af; background: rgba(127, 29, 29, .3); }.state-pill.waiting { color: #fde68a; background: rgba(120, 53, 15, .28); }.job-error, .job-history { margin: 6px 0 0; font-size: 12px; }.job-error { color: #fca5a5; }.job-history { color: #94a3b8; } .empty { display: grid; justify-items: center; gap: 10px; max-width: 1280px; margin: 0 auto; padding: 68px 24px; border: 1px dashed rgba(129, 140, 248, .34); border-radius: 16px; text-align: center; background: rgba(15, 23, 42, .35); }.empty-icon { width: 58px; height: 58px; }.empty h3 { margin: 4px 0 0; font-size: 18px; }.empty p { margin: 0 0 8px; color: var(--text-secondary); }
@keyframes spin { to { transform: rotate(360deg); } } @media (max-width: 760px) { .queue-header { display: grid; }.stats { grid-template-columns: 1fr; }.video-card { grid-template-columns: auto minmax(0, 1fr); }.video-actions { grid-column: 1 / -1; }.queue-screen { padding: 24px 16px 40px; } }
</style>
