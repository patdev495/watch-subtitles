<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Sparkles, PanelRightClose, PanelRightOpen } from 'lucide-vue-next';
import HeaderBar from './components/HeaderBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import TranscriptFooter from './components/TranscriptFooter.vue';
import SettingsModal from './components/SettingsModal.vue';
import SubtitleGenerationModal from './components/SubtitleGenerationModal.vue';
import PlaybackQueue from './components/PlaybackQueue.vue';
import { usePlaybackQueue } from './composables/usePlaybackQueue';
import { useSubtitleQueue } from './composables/useSubtitleQueue';
import { useTheme } from './composables/useTheme';
import { useSubtitleDisplayPreferences } from './composables/useSubtitleDisplayPreferences';
import { getMockCues } from './fixtures/mockCues';
import type { VideoDialogResponse, AppSettings, Cue, SubtitleJob, PlaybackVideo } from './types';
// ── Video state ──────────────────────────────────────────────────────────────
const videoSrc = ref<string>('');
const currentFilename = ref<string>('');
const backendConnected = ref<boolean>(false);
const isDragging = ref<boolean>(false);
const notifications = ref<{ id: string; message: string; failed: boolean }[]>([]);
const currentTime = ref<number>(0);
const duration = ref<number>(0);
let subtitleLoadToken = 0;
let videoOpenToken = 0;
// ── Pipeline & Subtitle state ────────────────────────────────────────────────
const sourceLanguage = ref<string>('en');
const targetLanguage = ref<string>('vi');
const hasSubtitles = ref<boolean>(false);
const isGenerating = ref<boolean>(false);
// ── Cue / Transcript state ───────────────────────────────────────────────────
const cues = ref<Cue[]>([]);
function loadMockCues(): void {
  cues.value = getMockCues();
}

const { loadTheme } = useTheme();

const {
  queuedVideos, currentFilePath, autoAdvance, restoreTime, hasPrevious, hasNext,
  restoreQueue, rememberOpenedVideo, importQueue, selectQueueVideo, setOpenedVideo, setVideoLanguages,
  recordSubtitleAvailability, markPlaybackError, removePlaybackVideo, clearPlaybackQueue,
  playNext, playPrevious, advanceQueue, handlePlaybackError,
} = usePlaybackQueue(currentTime, sourceLanguage, {
  openVideo: async (path, source, target, resumeAt) => handleOpenVideo(path, source, target, resumeAt),
  stopPlayback: () => {
    ++subtitleLoadToken;
    ++videoOpenToken;
    videoSrc.value = '';
    currentFilename.value = '';
    cues.value = [];
    hasSubtitles.value = false;
    duration.value = 0;
  },
  duplicateImport: (path) => {
    notifications.value.push({ id: `duplicate-${Date.now()}-${path}`, message: 'Video đã trong hàng đợi rồi.', failed: true });
  },
});

const { subtitleJobs, updateSubtitleJob, refreshSubtitleJobs, createSubtitleJob, generateAllQueuedVideos, retrySubtitleJob } = useSubtitleQueue(
  currentFilePath,
  (job, previous) => {
    if (job.status === 'completed') {
      recordSubtitleAvailability(job.video_path, job.source_language, job.target_language);
    }
    if (job.video_path === currentFilePath.value
      && job.source_language === sourceLanguage.value
      && job.target_language === targetLanguage.value) {
      if (job.status === 'completed') {
        cues.value = job.cues;
        hasSubtitles.value = job.cues.length > 0;
      }
    }
    if ((job.status === 'completed' || job.status === 'failed') && previous?.status !== job.status) {
      notifications.value.push({ id: job.id, message: job.status === 'completed' ? `Hoàn thành: ${job.video_path.split(/[/\\]/).pop()}` : `Lỗi: ${job.error}`, failed: job.status === 'failed' });
      setTimeout(() => { notifications.value = notifications.value.filter((item) => item.id !== job.id); }, 5000);
    }
  },
  isGenerating,
);

// ── Settings state ───────────────────────────────────────────────────────────
const settingsOpen = ref<boolean>(false);
const subtitlesModalOpen = ref(false);
const sidebarVisible = ref(true);
const { displayPreferences, loadDisplayPreferences, saveDisplayPreferences } = useSubtitleDisplayPreferences();
const settings = ref<AppSettings>({
  deepgram_api_key: '',
  assemblyai_api_key: '',
  deepl_api_key: '',
  default_target_language: 'vi',
  stt_provider: 'deepgram',
  translation_provider: 'deepl',
});

async function loadSettings(): Promise<void> {
  if (window.pywebview?.api?.get_settings) {
    try {
      settings.value = await window.pywebview.api.get_settings();
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  }
}

function handleSettingsSaved(saved: AppSettings): void {
  settings.value = saved;
}

// ── Backend bridge ───────────────────────────────────────────────────────────

async function checkBackendBridge(): Promise<void> {
  if (window.pywebview?.api) {
    try {
      const res = await window.pywebview.api.ping();
      backendConnected.value = res.status === 'ok';
    } catch (err) {
      console.error('Failed to ping pywebview api:', err);
    }
  } else {
    window.addEventListener('pywebviewready', async () => {
      if (window.pywebview?.api) {
        try {
          const res = await window.pywebview.api.ping();
          backendConnected.value = res.status === 'ok';
          await loadSettings();
          await loadDisplayPreferences();
          await loadTheme();
          await restoreQueue();
          await refreshSubtitleJobs();
        } catch (err) {
          console.error(err);
        }
      }
    });
  }
}

// ── Video file handling ──────────────────────────────────────────────────────

async function loadSubtitlesForVideo(filePath: string, source: string, target: string): Promise<void> {
  const token = ++subtitleLoadToken;
  hasSubtitles.value = false;
  cues.value = [];
  if (window.pywebview?.api && filePath) {
    try {
      const res = await window.pywebview.api.get_cached_subtitles(filePath, source, target);
      if (token !== subtitleLoadToken) return;
      hasSubtitles.value = res.cached && res.cues.length > 0;
      if (res.cached && res.cues && res.cues.length > 0) {
        cues.value = res.cues;
        return;
      }
    } catch (err) {
      console.warn('Error reading subtitle cache:', err);
    }
    if (token !== subtitleLoadToken) return;
    cues.value = [];
    return;
  }
  loadMockCues();
}

async function handleSourceLanguageChange(language: string): Promise<void> {
  sourceLanguage.value = language;
  const video = queuedVideos.value.find((item) => item.path === currentFilePath.value);
  if (video) setVideoLanguages(video, language, targetLanguage.value);
  if (currentFilePath.value) {
    await loadSubtitlesForVideo(currentFilePath.value, language, targetLanguage.value);
  }
}

function handleQueueSourceChange(video: PlaybackVideo, source: string): void {
  setVideoLanguages(video, source);
  if (video.path === currentFilePath.value) void handleSourceLanguageChange(source);
}

async function handleOpenVideo(videoPath?: string, source?: string, target?: string, resumeAt = 0): Promise<void> {
  if (!window.pywebview?.api) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'video/*';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        videoSrc.value = URL.createObjectURL(file);
        currentFilename.value = file.name;
        loadMockCues();
      }
    };
    input.click();
    return;
  }

  try {
    const openToken = ++videoOpenToken;
    const res: VideoDialogResponse = videoPath ? await window.pywebview.api.load_video_path(videoPath) : await window.pywebview.api.open_video_dialog();
    if (openToken !== videoOpenToken) return;
    if (!res.cancelled && res.stream_url && res.filename) {
      videoSrc.value = res.stream_url;
      currentFilename.value = res.filename;
      setOpenedVideo(res.path || '', resumeAt);
      const existing = queuedVideos.value.find((video) => video.path === currentFilePath.value);
      if (currentFilePath.value) {
        await rememberOpenedVideo(currentFilePath.value, res.filename, source, target, () => openToken === videoOpenToken);
      }
      if (openToken !== videoOpenToken) return;
      const selectedSource = source ?? existing?.sourceLanguage;
      const selectedTarget = target ?? existing?.targetLanguage;
      if (selectedSource && selectedTarget) {
        sourceLanguage.value = selectedSource;
        targetLanguage.value = selectedTarget;
        await loadSubtitlesForVideo(currentFilePath.value, selectedSource, selectedTarget);
      } else if (window.pywebview.api.get_latest_cached_subtitles) {
        const latest = await window.pywebview.api.get_latest_cached_subtitles(currentFilePath.value);
        if (openToken !== videoOpenToken) return;
        sourceLanguage.value = latest.cached && latest.source_language ? latest.source_language : selectedSource ?? sourceLanguage.value;
        targetLanguage.value = latest.cached && latest.target_language ? latest.target_language : selectedTarget ?? targetLanguage.value;
        cues.value = latest.cached ? latest.cues : [];
        hasSubtitles.value = cues.value.length > 0;
        const video = queuedVideos.value.find((item) => item.path === currentFilePath.value);
        if (video && latest.cached) {
          setVideoLanguages(video, sourceLanguage.value, targetLanguage.value);
        }
      } else {
        if (selectedSource) sourceLanguage.value = selectedSource;
        await loadSubtitlesForVideo(currentFilePath.value, sourceLanguage.value, targetLanguage.value);
      }
    }
    else if (videoPath) {
      markPlaybackError(videoPath);
    }
  } catch (err) {
    console.error('Lỗi khi mở video:', err);
    if (videoPath) markPlaybackError(videoPath);
  }
}

async function selectSubtitlePair(video: PlaybackVideo, source: string, target: string): Promise<void> {
  setVideoLanguages(video, source, target);
  if (video.path === currentFilePath.value) {
    ++videoOpenToken;
    sourceLanguage.value = source;
    targetLanguage.value = target;
    await loadSubtitlesForVideo(video.path, source, target);
  } else {
    await handleOpenVideo(video.path, source, target);
  }
}

async function handlePingBackend(): Promise<void> {
  if (window.pywebview?.api) {
    try {
      const res = await window.pywebview.api.ping();
      alert(`Bridge Ping Thành Công!\nTrạng thái: ${res.status}\nTin nhắn: ${res.message}`);
    } catch (err) {
      alert(`Lỗi Bridge Ping: ${err}`);
    }
  } else {
    alert('Chưa phát hiện pywebview bridge (Đang chạy dev server browser thông thường)');
  }
}

async function handleDrop(event: DragEvent): Promise<void> {
  isDragging.value = false;
  event.preventDefault();

  const files = event.dataTransfer?.files;
  if (!files || files.length === 0) return;

  const file = files[0];
  const anyFile = file as unknown as { path?: string };

  if (window.pywebview?.api && anyFile.path) {
    try {
      await handleOpenVideo(anyFile.path);
      if (currentFilePath.value === anyFile.path) return;
    } catch (err) {
      console.warn('Backend load path error, fallback to URL.createObjectURL', err);
    }
  }

  videoSrc.value = URL.createObjectURL(file);
  currentFilename.value = file.name;
  loadMockCues();
}

function handleDragOver(event: DragEvent): void {
  event.preventDefault();
  isDragging.value = true;
}

function handleDragLeave(): void {
  isDragging.value = false;
}

onMounted(() => {
  checkBackendBridge();
  if (window.pywebview?.api) {
    void loadSettings();
    void loadDisplayPreferences();
    void loadTheme();
    void restoreQueue();
  }
  window.addEventListener('subtitle-job-progress', (event: Event) => {
    updateSubtitleJob((event as CustomEvent<SubtitleJob>).detail);
  });
  void refreshSubtitleJobs();
});
</script>

<template>
  <div
    class="app-shell"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <!-- Drag overlay -->
    <div v-if="isDragging" class="drag-overlay">
      <div class="drag-halo-card">
        <Sparkles :size="18" class="drag-icon" />
        <h3>Thả video vào đây để nạp vào Studio</h3>
      </div>
    </div>

    <!-- Header bar -->
    <HeaderBar
      :current-filename="currentFilename"
      :backend-connected="backendConnected"
      :has-subtitles="hasSubtitles"
      @open-video="handleOpenVideo"
      @ping-backend="handlePingBackend"
      @open-settings="settingsOpen = true"
      @open-subtitles="subtitlesModalOpen = true"
    />

    <!-- Main Workspace -->
    <main class="flex-1 flex min-w-0 min-h-0 relative overflow-hidden bg-[var(--bg-base)]">
      <!-- Player Area (Center) -->
      <section class="flex-1 flex min-w-0 min-h-0 relative bg-[var(--bg-base)]">
        <VideoPlayer
          :src="videoSrc"
          :filename="currentFilename"
          :initial-time="restoreTime"
          :has-previous="hasPrevious"
          :has-next="hasNext"
          @timeupdate="t => currentTime = t"
          @durationchange="d => duration = d"
          @ended="advanceQueue"
          @error="handlePlaybackError"
          @open-file="handleOpenVideo"
          @previous="playPrevious"
          @next="playNext"
        >
          <template #default="{ isFullscreen, controlsVisible }">
            <TranscriptFooter
              :cues="cues"
              :current-time="currentTime"
              :source-language="sourceLanguage"
              :target-language="targetLanguage"
              :is-fullscreen="isFullscreen"
              :controls-visible="controlsVisible"
              :preferences="displayPreferences"
              @update:preferences="saveDisplayPreferences"
            />
          </template>
        </VideoPlayer>
      </section>

      <!-- Sidebar Toggle Floating Button when closed -->
      <button
        v-if="!sidebarVisible"
        class="absolute right-4 top-4 z-30 w-10 h-10 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-white shadow-lg grid place-items-center transition-all"
        title="Mở bảng điều khiển"
        @click="sidebarVisible = true"
      >
        <PanelRightOpen :size="18" />
      </button>

      <!-- Playback Queue Sidebar (Right) -->
      <aside
        class="flex flex-col transition-all duration-300 ease-in-out border-l border-[var(--border-subtle)] bg-[var(--bg-surface)] relative z-20"
        :style="{ width: sidebarVisible ? '360px' : '0px', opacity: sidebarVisible ? '1' : '0', overflow: 'hidden' }"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-[var(--border-subtle)]">
          <span class="font-semibold text-sm text-white flex items-center gap-2">
            Hàng đợi phát & Phụ đề
          </span>
          <button
            class="w-7 h-7 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-muted)] hover:text-white grid place-items-center transition-all"
            title="Đóng bảng điều khiển"
            @click="sidebarVisible = false"
          >
            <PanelRightClose :size="16" />
          </button>
        </div>
        <div class="flex-1 min-h-0 flex flex-col overflow-hidden">
          <PlaybackQueue
            :videos="queuedVideos"
            :jobs="subtitleJobs"
            :active-path="currentFilePath"
            :auto-advance="autoAdvance"
            @add-files="importQueue('files')"
            @add-folder="importQueue('folder')"
            @select="selectQueueVideo"
            @select-pair="selectSubtitlePair"
            @remove="removePlaybackVideo"
            @clear="clearPlaybackQueue"
            @update:auto-advance="autoAdvance = $event"
            @source-change="handleQueueSourceChange"
          />
        </div>
      </aside>
    </main>

    <SubtitleGenerationModal
      :open="subtitlesModalOpen"
      :videos="queuedVideos"
      :jobs="subtitleJobs"
      :active-path="currentFilePath"
      :default-target-language="settings.default_target_language || 'vi'"
      @close="subtitlesModalOpen = false"
      @generate="createSubtitleJob"
      @generate-all="generateAllQueuedVideos"
      @retry="retrySubtitleJob"
      @source-change="handleQueueSourceChange"
    />

    <!-- Settings Modal -->
    <SettingsModal
      v-model="settingsOpen"
      :initial-settings="settings"
      @saved="handleSettingsSaved"
    />
    <aside class="notifications" aria-live="polite">
      <button v-for="notice in notifications" :key="notice.id" :class="{ failed: notice.failed }" @click="notifications = notifications.filter(item => item.id !== notice.id)">
        {{ notice.message }}
      </button>
      <span v-for="video in queuedVideos.filter(item => item.error)" :key="video.path" class="queue-error-toast">{{ video.error }}</span>
    </aside>
  </div>
</template>

<style scoped src="./App.css"></style>
