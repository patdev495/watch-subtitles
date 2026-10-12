<script setup lang="ts">
import { watch } from 'vue';
import type { PlaybackVideo, SubtitleJob } from '../types';
import { Film, FolderPlus, ListPlus, Play, Trash2, X } from 'lucide-vue-next';
import { useThumbnails } from '../composables/useThumbnails';

const props = defineProps<{
  videos: PlaybackVideo[];
  jobs: SubtitleJob[];
  activePath: string;
  autoAdvance: boolean;
}>();
const emit = defineEmits<{
  (event: 'select', video: PlaybackVideo): void;
  (event: 'select-pair', video: PlaybackVideo, source: string, target: string): void;
  (event: 'remove', video: PlaybackVideo): void;
  (event: 'clear'): void;
  (event: 'add-files'): void;
  (event: 'add-folder'): void;
  (event: 'update:autoAdvance', enabled: boolean): void;
  (event: 'source-change', video: PlaybackVideo, source: string): void;
}>();

const { loadThumbnail, failThumbnail, thumbnailUrl } = useThumbnails();
watch(() => props.videos, (videos) => { for (const video of videos) void loadThumbnail(video.path); }, { immediate: true, deep: true });

function currentJob(jobs: SubtitleJob[], path: string): SubtitleJob | undefined {
  return jobs.filter((job) => job.video_path === path && ['waiting', 'processing'].includes(job.status)).at(-1);
}
</script>

<template>
  <aside class="playback-queue" aria-label="Thư viện video">
    <header class="queue-header">
      <div class="queue-heading">
        <h2>Thư viện</h2>
        <span class="count-badge">{{ videos.length }}</span>
      </div>
      <div class="queue-actions">
        <button aria-label="Thêm video" title="Thêm video" @click="emit('add-files')">
          <ListPlus :size="16" :stroke-width="1.75" aria-hidden="true" />
        </button>
        <button aria-label="Thêm thư mục" title="Thêm thư mục" @click="emit('add-folder')">
          <FolderPlus :size="16" :stroke-width="1.75" aria-hidden="true" />
        </button>
        <button
          class="clear-queue"
          aria-label="Xóa tất cả video khỏi hàng đợi phát"
          title="Xóa tất cả"
          :disabled="videos.length === 0"
          @click="emit('clear')"
        >
          <Trash2 :size="16" :stroke-width="1.75" aria-hidden="true" />
        </button>
      </div>
    </header>

    <div v-if="videos.length === 0" class="empty-state">
      <span class="empty-icon" aria-hidden="true"><Film :size="26" :stroke-width="1.5" /></span>
      <p class="empty">Chưa có video.</p>
      <span class="empty-hint">Kéo thả video vào đây để bắt đầu</span>
      <button class="empty-action" @click="emit('add-files')">
        <ListPlus :size="16" :stroke-width="1.75" aria-hidden="true" />
        <span>Chọn video</span>
      </button>
    </div>

    <ol v-else class="video-list">
      <li
        v-for="video in videos"
        :key="video.path"
        :data-test="video.path === activePath ? 'queue-row-active' : 'queue-row'"
        :class="{ active: video.path === activePath, failed: Boolean(video.error) }"
      >
        <button class="queue-select" :aria-label="`Phát ${video.filename}`" @click="emit('select', video)">
          <span class="queue-thumb">
            <img
              v-if="thumbnailUrl(video.path)"
              :src="thumbnailUrl(video.path)"
              alt=""
              loading="lazy"
              @error="failThumbnail(video.path)"
            />
            <span v-else class="thumb-fallback" aria-hidden="true"><Film :size="18" :stroke-width="1.5" /></span>
            <span v-if="video.path === activePath" class="thumb-playing" aria-hidden="true">
              <Play :size="14" :stroke-width="2.5" />
            </span>
            <span
              v-if="currentJob(jobs, video.path)"
              class="job-indicator"
              :title="currentJob(jobs, video.path)?.status === 'processing' ? `${currentJob(jobs, video.path)?.progress}%` : 'Đang chờ'"
              aria-label="Đang tạo phụ đề"
            >
              <span class="job-spinner" aria-hidden="true"></span>
              <span v-if="currentJob(jobs, video.path)?.status === 'processing'">{{ Math.round(currentJob(jobs, video.path)?.progress ?? 0) }}%</span>
              <span v-else>Đang chờ</span>
            </span>
            <span
              v-if="currentJob(jobs, video.path)?.status === 'processing'"
              class="thumb-progress"
              :style="{ width: `${Math.min(100, Math.max(0, currentJob(jobs, video.path)?.progress ?? 0))}%` }"
              aria-hidden="true"
            ></span>
          </span>
        </button>
        <span class="row-body">
          <button
            class="filename"
            :data-test="`queue-select-${video.filename.charAt(0)}`"
            :title="video.filename"
            @click="emit('select', video)"
          >{{ video.filename }}</button>
          <span class="row-meta">
            <template v-if="video.cachedPairs?.length">
              <button
                v-for="([source, target], index) in video.cachedPairs"
                :key="`${source}-${target}-${index}`"
                class="language-badge"
                :class="{ selected: video.sourceLanguage === source && video.targetLanguage === target }"
                :aria-label="`Hiển thị phụ đề ${source.toUpperCase()} sang ${target.toUpperCase()} cho ${video.filename}`"
                :aria-pressed="video.sourceLanguage === source && video.targetLanguage === target"
                @click="emit('select-pair', video, source, target)"
              >{{ source.toUpperCase() }}→{{ target.toUpperCase() }}</button>
            </template>
            <span v-else class="no-subtitles">Chưa có phụ đề</span>
            <span v-if="video.error" class="row-error" :title="video.error" aria-label="Lỗi video">Lỗi</span>
          </span>
        </span>
        <button
          class="queue-remove"
          :data-test="`queue-remove-${video.filename.charAt(0)}`"
          :aria-label="`Xóa ${video.filename}`"
          :title="`Xóa ${video.filename}`"
          @click="emit('remove', video)"
        >
          <X :size="15" :stroke-width="2" aria-hidden="true" />
        </button>
      </li>
    </ol>

    <footer class="queue-footer">
      <label class="auto-advance">
        <input
          type="checkbox"
          :checked="autoAdvance"
          @change="emit('update:autoAdvance', ($event.target as HTMLInputElement).checked)"
        />
        <span>Tự chuyển video</span>
      </label>
    </footer>
  </aside>
</template>

<style scoped src="./PlaybackQueue.css"></style>
