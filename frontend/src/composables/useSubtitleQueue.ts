import { computed, ref, type Ref } from 'vue';
import type { SubtitleJob } from '../types';
import type { QueuedVideo, QueueGenerationRequest } from '../components/QueueScreen.vue';

export function useSubtitleQueue(currentPath: Ref<string>, onJobUpdate: (job: SubtitleJob) => void, isGenerating: Ref<boolean>) {
  const activeScreen = ref<'player' | 'queue'>('player');
  const queuedVideos = ref<QueuedVideo[]>([]);
  const subtitleJobs = ref<SubtitleJob[]>([]);
  const activeMainJob = computed(() => subtitleJobs.value.find(
    (job) => job.video_path === currentPath.value && ['waiting', 'processing'].includes(job.status),
  ));

  function updateSubtitleJob(job: SubtitleJob): void {
    const index = subtitleJobs.value.findIndex((item) => item.id === job.id);
    const previous = index === -1 ? undefined : subtitleJobs.value[index];
    if (index === -1) subtitleJobs.value.push(job);
    else subtitleJobs.value[index] = job;
    if (previous?.status !== job.status || index === -1) onJobUpdate(job);
    if (job.status === 'completed') {
      const video = queuedVideos.value.find((item) => item.path === job.video_path);
      if (video && !video.cachedPairs?.some(([source, target]) => source === job.source_language && target === job.target_language)) {
        video.cachedPairs = [...(video.cachedPairs ?? []), [job.source_language, job.target_language]];
      }
    }
    isGenerating.value = Boolean(activeMainJob.value);
  }

  async function refreshSubtitleJobs(): Promise<void> {
    const result = await window.pywebview?.api?.list_subtitle_jobs();
    if (result?.ok) subtitleJobs.value = result.jobs;
  }

  async function createSubtitleJob(video: QueuedVideo, source: string, target: string): Promise<void> {
    const result = await window.pywebview?.api?.create_subtitle_job(video.path, source, target);
    if (result?.job) updateSubtitleJob(result.job);
    if (!result?.ok) alert(result?.error || 'Không thể tạo Subtitle Job.');
  }

  async function addQueuedVideo(): Promise<void> {
    const api = window.pywebview?.api;
    if (!api) return;
    const result = await api.open_video_dialog();
    if (result.cancelled || !result.path || !result.filename) return;
    if (queuedVideos.value.some((video) => video.path === result.path)) return;
    const cached = await api.get_cached_subtitle_languages(result.path);
    queuedVideos.value.push({ path: result.path, filename: result.filename, cachedPairs: cached.ok ? cached.language_pairs : [] });
  }

  async function generateAllQueuedVideos(requests: QueueGenerationRequest[]): Promise<void> {
    for (const { video, source, target } of requests) {
      const active = subtitleJobs.value.some((job) => job.video_path === video.path && ['waiting', 'processing'].includes(job.status));
      if (!active) await createSubtitleJob(video, source, target);
    }
  }

  async function retrySubtitleJob(jobId: string): Promise<void> {
    const result = await window.pywebview?.api?.retry_subtitle_job(jobId);
    if (result?.job) updateSubtitleJob(result.job);
  }

  async function removeSubtitleJob(jobId: string): Promise<void> {
    const result = await window.pywebview?.api?.remove_subtitle_job(jobId);
    if (result?.job) updateSubtitleJob(result.job);
  }

  function removeQueuedVideo(video: QueuedVideo): void {
    queuedVideos.value = queuedVideos.value.filter((item) => item.path !== video.path);
  }

  return { activeScreen, queuedVideos, subtitleJobs, updateSubtitleJob, refreshSubtitleJobs, createSubtitleJob, addQueuedVideo, generateAllQueuedVideos, retrySubtitleJob, removeSubtitleJob, removeQueuedVideo };
}
