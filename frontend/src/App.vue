<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Sparkles } from 'lucide-vue-next';
import HeaderBar from './components/HeaderBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import TranscriptFooter from './components/TranscriptFooter.vue';
import SettingsModal from './components/SettingsModal.vue';
import PipelineProgressBar from './components/PipelineProgressBar.vue';
import QueueScreen from './components/QueueScreen.vue';
import { useSubtitleQueue } from './composables/useSubtitleQueue';
import { getMockCues } from './fixtures/mockCues';
import type { VideoDialogResponse, AppSettings, Cue, PipelineStatus, SubtitleJob } from './types';
// ── Video state ──────────────────────────────────────────────────────────────
const videoSrc = ref<string>('');
const currentFilename = ref<string>('');
const currentFilePath = ref<string>('');
const backendConnected = ref<boolean>(false);
const isDragging = ref<boolean>(false);
const notifications = ref<{ id: string; message: string; failed: boolean }[]>([]);
const currentTime = ref<number>(0);
const duration = ref<number>(0);
// ── Pipeline & Subtitle state ────────────────────────────────────────────────
const sourceLanguage = ref<string>('en');
const targetLanguage = ref<string>('vi');
const hasSubtitles = ref<boolean>(false);
const isGenerating = ref<boolean>(false);
const showPipelineProgress = ref<boolean>(false);
const pipelineStatus = ref<PipelineStatus>({
  status: 'idle',
  progress: 0,
  step: '',
  cues: [],
  error: null,
});
// ── Cue / Transcript state ───────────────────────────────────────────────────
const cues = ref<Cue[]>([]);
function loadMockCues(): void {
  cues.value = getMockCues();
}

const { activeScreen, queuedVideos, subtitleJobs, updateSubtitleJob, refreshSubtitleJobs, createSubtitleJob, addQueuedVideo, generateAllQueuedVideos, retrySubtitleJob, removeSubtitleJob, removeQueuedVideo } = useSubtitleQueue(
  currentFilePath,
  (job, previous) => {
    if (job.video_path === currentFilePath.value
      && job.source_language === sourceLanguage.value
      && job.target_language === targetLanguage.value) {
      showPipelineProgress.value = true;
      pipelineStatus.value = { status: job.status === 'completed' ? 'completed' : job.status === 'failed' || job.status === 'cancelled' ? 'error' : 'running', progress: job.progress, step: job.step, cues: job.cues, error: job.error };
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
const settings = ref<AppSettings>({
  deepgram_api_key: '',
  assemblyai_api_key: '',
  deepl_api_key: '',
  default_target_language: 'vi',
  stt_provider: 'deepgram',
  translation_provider: 'deepl',
});

async function loadSettings(): Promise<void> {
  if (window.pywebview?.api) {
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
        } catch (err) {
          console.error(err);
        }
      }
    });
  }
}

// ── Video file handling ──────────────────────────────────────────────────────

async function loadSubtitlesForVideo(filePath: string, source: string, target: string): Promise<void> {
  hasSubtitles.value = false;
  if (window.pywebview?.api && filePath) {
    try {
      const res = await window.pywebview.api.get_cached_subtitles(filePath, source, target);
      hasSubtitles.value = res.cached && res.cues.length > 0;
      if (res.cached && res.cues && res.cues.length > 0) {
        cues.value = res.cues;
        return;
      }
    } catch (err) {
      console.warn('Error reading subtitle cache:', err);
    }
    cues.value = [];
    return;
  }
  loadMockCues();
}

async function handleSourceLanguageChange(language: string): Promise<void> {
  sourceLanguage.value = language;
  if (currentFilePath.value) {
    await loadSubtitlesForVideo(currentFilePath.value, language, targetLanguage.value);
  }
}

async function handleTargetLanguageChange(language: string): Promise<void> {
  targetLanguage.value = language;
  if (currentFilePath.value) {
    await loadSubtitlesForVideo(currentFilePath.value, sourceLanguage.value, language);
  }
}

async function handleGenerateSubtitles(source: string, target: string, force: boolean): Promise<void> {
  if (!currentFilePath.value && !window.pywebview?.api) {
    // Dev browser simulation
    isGenerating.value = true;
    showPipelineProgress.value = true;
    pipelineStatus.value = {
      status: 'running',
      progress: 20,
      step: 'Đang trích xuất audio (Mô phỏng)...',
      cues: [],
      error: null,
    };
    setTimeout(() => {
      pipelineStatus.value = {
        status: 'running',
        progress: 60,
        step: 'Đang nhận diện Deepgram (Mô phỏng)...',
        cues: [],
        error: null,
      };
    }, 600);
    setTimeout(() => {
      pipelineStatus.value = {
        status: 'completed',
        progress: 100,
        step: 'Hoàn thành!',
        cues: getMockCues(),
        error: null,
      };
      cues.value = getMockCues();
      isGenerating.value = false;
    }, 1200);
    return;
  }

  if (!currentFilePath.value) {
    alert('Vui lòng chọn video trước khi tạo phụ đề.');
    return;
  }

  if (window.pywebview?.api) {
    if (force) {
      cues.value = [];
      hasSubtitles.value = false;
    }
    await createSubtitleJob({ path: currentFilePath.value, filename: currentFilename.value }, source, target, force);
    return;
  }
}

async function handleOpenVideo(videoPath?: string, source?: string, target?: string): Promise<void> {
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
        activeScreen.value = 'player';
      }
    };
    input.click();
    return;
  }

  try {
    const res: VideoDialogResponse = videoPath ? await window.pywebview.api.load_video_path(videoPath) : await window.pywebview.api.open_video_dialog();
    if (!res.cancelled && res.stream_url && res.filename) {
      if (source) sourceLanguage.value = source;
      if (target) targetLanguage.value = target;
      videoSrc.value = res.stream_url;
      currentFilename.value = res.filename;
      currentFilePath.value = res.path || '';
      await loadSubtitlesForVideo(currentFilePath.value, sourceLanguage.value, targetLanguage.value);
      activeScreen.value = 'player';
    }
  } catch (err) {
    console.error('Lỗi khi mở video:', err);
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
      const res = await window.pywebview.api.load_video_path(anyFile.path);
      if (!res.cancelled && res.stream_url) {
        videoSrc.value = res.stream_url;
        currentFilename.value = res.filename ?? file.name;
        currentFilePath.value = anyFile.path;
        await loadSubtitlesForVideo(currentFilePath.value, sourceLanguage.value, targetLanguage.value);
        return;
      }
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
        <Sparkles :size="36" class="drag-icon" />
        <h3>Thả video vào đây để nạp vào Studio</h3>
      </div>
    </div>

    <!-- Header bar -->
    <HeaderBar
      :source-language="sourceLanguage"
      :target-language="targetLanguage"
      @update:source-language="handleSourceLanguageChange"
      @update:target-language="handleTargetLanguageChange"
      :current-filename="currentFilename"
      :backend-connected="backendConnected"
      :is-generating="isGenerating"
      :has-subtitles="hasSubtitles"
      @open-video="handleOpenVideo"
      @ping-backend="handlePingBackend"
      @open-settings="settingsOpen = true"
      @open-queue="activeScreen = activeScreen === 'queue' ? 'player' : 'queue'"
      @generate-subtitles="handleGenerateSubtitles"
    />

    <!-- Main Workspace -->
    <QueueScreen
      v-if="activeScreen === 'queue'"
      :videos="queuedVideos"
      :jobs="subtitleJobs"
      :source-language="sourceLanguage"
      :target-language="targetLanguage"
      @add="addQueuedVideo"
      @generate="createSubtitleJob"
      @generate-all="generateAllQueuedVideos"
      @play="(video, source, target) => handleOpenVideo(video.path, source, target)"
      @retry="retrySubtitleJob"
      @remove-job="removeSubtitleJob"
      @remove-video="removeQueuedVideo"
      @back="activeScreen = 'player'"
    />
    <main v-else class="studio-workspace">
      <!-- Player Area -->
      <section class="player-wrapper">
        <VideoPlayer
          :src="videoSrc"
          :filename="currentFilename"
          @timeupdate="t => currentTime = t"
          @durationchange="d => duration = d"
          @open-file="handleOpenVideo"
        >
          <template #default="{ isFullscreen, controlsVisible }">
            <TranscriptFooter
              :cues="cues"
              :current-time="currentTime"
              :source-language="sourceLanguage"
              :target-language="targetLanguage"
              :is-fullscreen="isFullscreen"
              :controls-visible="controlsVisible"
            />
          </template>
        </VideoPlayer>
      </section>
    </main>

    <!-- Pipeline Progress Modal -->
    <PipelineProgressBar
      v-model="showPipelineProgress"
      :status="pipelineStatus"
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
    </aside>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: var(--bg-base);
  position: relative;
  overflow: hidden;
}

.studio-workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 18px 24px 20px;
  gap: 16px;
  min-height: 0;
}

.player-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 0;
}

/* Drag & Drop Overlay */
.drag-overlay {
  position: absolute;
  inset: 0;
  background: rgba(3, 7, 18, 0.88);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  pointer-events: none;
}

.drag-halo-card {
  padding: 40px 60px;
  border: 2px dashed #6366f1;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.95);
  box-shadow: 0 0 50px rgba(99, 102, 241, 0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  color: #e2e8f0;
}

.notifications { position: fixed; right: 20px; bottom: 20px; display: grid; gap: 8px; z-index: 1100; }
.notifications button { max-width: 360px; padding: 10px 14px; text-align: left; color: #d1fae5; background: #064e3b; border: 1px solid #10b981; border-radius: 8px; cursor: pointer; }
.notifications button.failed { color: #fee2e2; background: #450a0a; border-color: #ef4444; }

.drag-icon {
  color: #38bdf8;
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.8; }
}
</style>
