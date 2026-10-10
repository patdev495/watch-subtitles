<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { Sparkles } from 'lucide-vue-next';
import HeaderBar from './components/HeaderBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import TranscriptFooter from './components/TranscriptFooter.vue';
import SettingsModal from './components/SettingsModal.vue';
import SubtitleGenerationModal from './components/SubtitleGenerationModal.vue';
import PlaybackQueue from './components/PlaybackQueue.vue';
import { useSubtitleQueue } from './composables/useSubtitleQueue';
import { getMockCues } from './fixtures/mockCues';
import type { VideoDialogResponse, AppSettings, Cue, SubtitleJob, PlaybackVideo, PlaybackQueueState, SubtitleDisplayPreferences } from './types';
// ── Video state ──────────────────────────────────────────────────────────────
const videoSrc = ref<string>('');
const currentFilename = ref<string>('');
const currentFilePath = ref<string>('');
const backendConnected = ref<boolean>(false);
const isDragging = ref<boolean>(false);
const notifications = ref<{ id: string; message: string; failed: boolean }[]>([]);
const currentTime = ref<number>(0);
const duration = ref<number>(0);
const autoAdvance = ref(true);
const restored = ref(false);
const restoreTime = ref(0);
let persistTimer: ReturnType<typeof setTimeout> | undefined;
let persistPending: Promise<void> = Promise.resolve();
let subtitleLoadToken = 0;
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

const { queuedVideos, subtitleJobs, updateSubtitleJob, refreshSubtitleJobs, createSubtitleJob, generateAllQueuedVideos, retrySubtitleJob } = useSubtitleQueue(
  currentFilePath,
  (job, previous) => {
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
const displayPreferences = ref<SubtitleDisplayPreferences>({
  primary_line: 'translated', overlay_visible: true,
  lines: {
    original: { visible: true, font_size: 20 }, originalPinyin: { visible: true, font_size: 15 },
    translated: { visible: true, font_size: 18 }, translatedPinyin: { visible: true, font_size: 15 },
  },
});
let displaySavePending: Promise<void> = Promise.resolve();
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

function queueState(): PlaybackQueueState {
  return {
    videos: queuedVideos.value.map((video) => ({ path: video.path, source_language: video.sourceLanguage ?? 'en' })),
    selected_path: currentFilePath.value,
    playback_time: currentTime.value,
    auto_advance: autoAdvance.value,
  };
}

function saveQueue(): void {
  const api = window.pywebview?.api;
  if (!restored.value || !api?.save_playback_queue) return;
  const snapshot = queueState();
  persistPending = persistPending.then(async () => { await api.save_playback_queue(snapshot); }).catch((error: unknown) => { console.error('Failed to save Playback Queue:', error); });
}

async function loadDisplayPreferences(): Promise<void> {
  const api = window.pywebview?.api;
  if (!api?.get_subtitle_display_preferences) return;
  try { displayPreferences.value = await api.get_subtitle_display_preferences(); }
  catch (error) { console.error('Failed to restore subtitle display preferences:', error); }
}

function saveDisplayPreferences(preferences: SubtitleDisplayPreferences): void {
  displayPreferences.value = preferences;
  const api = window.pywebview?.api;
  if (!api?.save_subtitle_display_preferences) return;
  displaySavePending = displaySavePending.then(async () => {
    await api.save_subtitle_display_preferences(preferences);
  }).catch((error: unknown) => { console.error('Failed to save subtitle display preferences:', error); });
}

function savePlaybackTime(): void {
  if (!restored.value || !window.pywebview?.api?.save_playback_queue) return;
  if (persistTimer) clearTimeout(persistTimer);
  persistTimer = setTimeout(saveQueue, 250);
}

watch([queuedVideos, currentFilePath, autoAdvance], saveQueue, { deep: true });
watch(currentTime, savePlaybackTime);

async function restoreQueue(): Promise<void> {
  const api = window.pywebview?.api;
  if (!api) return;
  if (!api.get_playback_queue) { restored.value = true; return; }
  try {
    const state = await api.get_playback_queue();
    autoAdvance.value = state.auto_advance;
    for (const video of state.videos) {
      const cached = await api.get_cached_subtitle_languages(video.path);
      queuedVideos.value.push({ path: video.path, filename: video.path.split(/[/\\]/).pop() ?? video.path, sourceLanguage: video.source_language, cachedPairs: cached.ok ? cached.language_pairs : [] });
    }
    if (state.selected_path) {
      restoreTime.value = state.playback_time;
      await handleOpenVideo(state.selected_path, queuedVideos.value.find((video) => video.path === state.selected_path)?.sourceLanguage, undefined, state.playback_time);
    }
  } catch (error) { console.error('Failed to restore Playback Queue:', error); }
  finally { restored.value = true; }
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
    cues.value = [];
    return;
  }
  loadMockCues();
}

async function handleSourceLanguageChange(language: string): Promise<void> {
  sourceLanguage.value = language;
  const video = queuedVideos.value.find((item) => item.path === currentFilePath.value);
  if (video) video.sourceLanguage = language;
  if (currentFilePath.value) {
    await loadSubtitlesForVideo(currentFilePath.value, language, targetLanguage.value);
  }
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
    const res: VideoDialogResponse = videoPath ? await window.pywebview.api.load_video_path(videoPath) : await window.pywebview.api.open_video_dialog();
    if (!res.cancelled && res.stream_url && res.filename) {
      restoreTime.value = resumeAt;
      currentTime.value = resumeAt;
      if (source) sourceLanguage.value = source;
      if (target) targetLanguage.value = target;
      videoSrc.value = res.stream_url;
      currentFilename.value = res.filename;
      currentFilePath.value = res.path || '';
      const existing = queuedVideos.value.find((video) => video.path === currentFilePath.value);
      if (!existing && currentFilePath.value) {
        const cached = await window.pywebview.api.get_cached_subtitle_languages?.(currentFilePath.value);
        queuedVideos.value.push({ path: currentFilePath.value, filename: res.filename, sourceLanguage: source ?? sourceLanguage.value, cachedPairs: cached?.ok ? cached.language_pairs : [] });
      }
      if (existing) {
        existing.error = undefined;
        if (source) existing.sourceLanguage = source;
        sourceLanguage.value = existing.sourceLanguage ?? sourceLanguage.value;
      }
      if (window.pywebview.api.get_latest_cached_subtitles) {
        const latest = await window.pywebview.api.get_latest_cached_subtitles(currentFilePath.value);
        sourceLanguage.value = latest.cached && latest.source_language ? latest.source_language : sourceLanguage.value;
        targetLanguage.value = latest.cached && latest.target_language ? latest.target_language : targetLanguage.value;
        cues.value = latest.cached ? latest.cues : [];
        hasSubtitles.value = cues.value.length > 0;
      } else {
        await loadSubtitlesForVideo(currentFilePath.value, sourceLanguage.value, targetLanguage.value);
      }
    }
    else if (videoPath) {
      const video = queuedVideos.value.find((item) => item.path === videoPath);
      if (video) video.error = 'Không thể phát video.';
    }
  } catch (err) {
    console.error('Lỗi khi mở video:', err);
    const video = queuedVideos.value.find((item) => item.path === videoPath);
    if (video) video.error = 'Không thể phát video.';
  }
}

async function importQueue(kind: 'files' | 'folder'): Promise<void> {
  const api = window.pywebview?.api;
  if (!api) return;
  const result = kind === 'files'
    ? (api.open_video_files_dialog ? await api.open_video_files_dialog() : { cancelled: false, videos: [await api.open_video_dialog()] })
    : await api.open_video_folder_dialog();
  if (result.cancelled) return;
  for (const entry of result.videos) {
    if (!entry.path || !entry.filename) continue;
    if (queuedVideos.value.some((video) => video.path === entry.path)) {
      notifications.value.push({ id: `duplicate-${Date.now()}-${entry.path}`, message: 'Video đã trong hàng đợi rồi.', failed: true });
      continue;
    }
    const cached = await api.get_cached_subtitle_languages(entry.path);
    queuedVideos.value.push({ path: entry.path, filename: entry.filename, sourceLanguage: sourceLanguage.value, cachedPairs: cached.ok ? cached.language_pairs : [] });
  }
}

async function selectQueueVideo(video: PlaybackVideo): Promise<void> {
  restoreTime.value = 0;
  await handleOpenVideo(video.path, video.sourceLanguage);
}

async function removePlaybackVideo(video: PlaybackVideo): Promise<void> {
  const index = queuedVideos.value.findIndex((item) => item.path === video.path);
  if (index < 0) return;
  const wasActive = currentFilePath.value === video.path;
  queuedVideos.value.splice(index, 1);
  if (wasActive) {
    videoSrc.value = ''; currentFilePath.value = ''; currentFilename.value = '';
    cues.value = []; currentTime.value = 0; restoreTime.value = 0;
    const next = queuedVideos.value[index] ?? queuedVideos.value[0];
    if (next) await selectQueueVideo(next as PlaybackVideo);
  }
}

function clearPlaybackQueue(): void {
  if (queuedVideos.value.length === 0) return;
  ++subtitleLoadToken;
  queuedVideos.value = [];
  videoSrc.value = '';
  currentFilePath.value = '';
  currentFilename.value = '';
  cues.value = [];
  hasSubtitles.value = false;
  currentTime.value = 0;
  duration.value = 0;
  restoreTime.value = 0;
}

async function advanceQueue(): Promise<void> {
  if (!autoAdvance.value) return;
  const index = queuedVideos.value.findIndex((video) => video.path === currentFilePath.value);
  for (const video of queuedVideos.value.slice(index + 1)) {
    await selectQueueVideo(video as PlaybackVideo);
    if (currentFilePath.value === video.path && !video.error) return;
  }
}

function handlePlaybackError(): void {
  const video = queuedVideos.value.find((item) => item.path === currentFilePath.value);
  if (video) video.error = 'Không thể phát video.';
  void advanceQueue();
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
  if (window.pywebview?.api) {
    void loadSettings();
    void loadDisplayPreferences();
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
        <Sparkles :size="36" class="drag-icon" />
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
    <main class="studio-workspace">
      <PlaybackQueue
        :videos="queuedVideos"
        :jobs="subtitleJobs"
        :active-path="currentFilePath"
        :auto-advance="autoAdvance"
        @add-files="importQueue('files')"
        @add-folder="importQueue('folder')"
        @select="selectQueueVideo"
        @remove="removePlaybackVideo"
        @clear="clearPlaybackQueue"
        @update:auto-advance="autoAdvance = $event"
        @source-change="(video, source) => { video.sourceLanguage = source; if (video.path === currentFilePath) handleSourceLanguageChange(source); }"
      />
      <!-- Player Area -->
      <section class="player-wrapper">
        <VideoPlayer
          :src="videoSrc"
          :filename="currentFilename"
          :initial-time="restoreTime"
          @timeupdate="t => currentTime = t"
          @durationchange="d => duration = d"
          @ended="advanceQueue"
          @error="handlePlaybackError"
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
              :preferences="displayPreferences"
              @update:preferences="saveDisplayPreferences"
            />
          </template>
        </VideoPlayer>
      </section>
    </main>

    <SubtitleGenerationModal
      :open="subtitlesModalOpen"
      :videos="queuedVideos"
      :jobs="subtitleJobs"
      :default-target-language="settings.default_target_language"
      @close="subtitlesModalOpen = false"
      @generate="createSubtitleJob"
      @generate-all="generateAllQueuedVideos"
      @retry="retrySubtitleJob"
      @source-change="(video, source) => { video.sourceLanguage = source; }"
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

<style scoped src="./App.css"></style>
