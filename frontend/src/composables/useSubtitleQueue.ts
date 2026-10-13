import { computed, ref, type Ref } from 'vue';
import type { PlaybackVideo, SubtitleJob } from '../types';

export interface QueueGenerationRequest { video: PlaybackVideo; source: string; target: string; force: boolean }

export function useSubtitleQueue(currentPath: Ref<string>, onJobUpdate: (job: SubtitleJob, previous?: SubtitleJob) => void, isGenerating: Ref<boolean>) {
  const subtitleJobs = ref<SubtitleJob[]>([]);
  const activeMainJob = computed(() => subtitleJobs.value.find(
    (job) => job.video_path === currentPath.value && ['waiting', 'processing'].includes(job.status),
  ));

  function updateSubtitleJob(job: SubtitleJob): void {
    const index = subtitleJobs.value.findIndex((item) => item.id === job.id);
    const previous = index === -1 ? undefined : subtitleJobs.value[index];
    if (index === -1) subtitleJobs.value.push(job);
    else subtitleJobs.value[index] = job;
    onJobUpdate(job, previous);
    isGenerating.value = Boolean(activeMainJob.value);
  }

  async function refreshSubtitleJobs(): Promise<void> {
    const result = await window.pywebview?.api?.list_subtitle_jobs();
    if (result?.ok) subtitleJobs.value = result.jobs;
  }

  async function createSubtitleJob(video: PlaybackVideo, source: string, target: string, force = false): Promise<void> {
    if (subtitleJobs.value.some((job) => job.video_path === video.path && job.source_language === source && job.target_language === target && ['waiting', 'processing'].includes(job.status))) return;
    const result = await window.pywebview?.api?.create_subtitle_job(video.path, source, target, force);
    if (result?.job) updateSubtitleJob(result.job);
    if (!result?.ok) alert(result?.error || 'Không thể tạo Subtitle Job.');
  }

  async function generateAllQueuedVideos(requests: QueueGenerationRequest[]): Promise<void> {
    for (const { video, source, target, force } of requests) {
      const cached = video.cachedPairs?.some(([cachedSource, cachedTarget]) => cachedSource === source && cachedTarget === target);
      if (!cached) await createSubtitleJob(video, source, target, force);
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

  return { subtitleJobs, activeMainJob, updateSubtitleJob, refreshSubtitleJobs, createSubtitleJob, generateAllQueuedVideos, retrySubtitleJob, removeSubtitleJob };
}
