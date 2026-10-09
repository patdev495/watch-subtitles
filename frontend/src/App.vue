<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Sparkles } from 'lucide-vue-next';
import HeaderBar from './components/HeaderBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import TranscriptFooter from './components/TranscriptFooter.vue';
import SettingsModal from './components/SettingsModal.vue';
import type { VideoDialogResponse, AppSettings, Cue } from './types';

// ── Video state ──────────────────────────────────────────────────────────────

const videoSrc = ref<string>('');
const currentFilename = ref<string>('');
const backendConnected = ref<boolean>(false);
const isDragging = ref<boolean>(false);

const currentTime = ref<number>(0);
const duration = ref<number>(0);

// ── Cue / Transcript state ───────────────────────────────────────────────────

const cues = ref<Cue[]>([]);

function loadMockCues(): void {
  const lines = [
    ['Hello, welcome to Watch Subtitles Studio.', 'Xin chào, chào mừng đến với Watch Subtitles Studio.'],
    ['This is a demonstration of the bilingual transcript footer.', 'Đây là bản demo của thanh phụ đề song ngữ.'],
    ['Each cue displays the original and translated text.', 'Mỗi dòng cue hiển thị văn bản gốc và bản dịch.'],
    ['Click any cue to seek the video to that moment.', 'Nhấp vào bất kỳ cue nào để tua video đến thời điểm đó.'],
    ['The active cue is highlighted automatically.', 'Cue đang phát được tô sáng tự động.'],
    ['Auto-scroll keeps the active cue in view.', 'Cuộn tự động giữ cue đang phát trong tầm nhìn.'],
    ['You can also drag and drop a video file onto this window.', 'Bạn cũng có thể kéo thả tệp video vào cửa sổ này.'],
    ['The backend is powered by Python with UV.', 'Backend được chạy bằng Python với UV.'],
    ['Deepgram handles speech-to-text transcription.', 'Deepgram xử lý chuyển đổi giọng nói thành văn bản.'],
    ['DeepL handles bilingual translation.', 'DeepL xử lý dịch song ngữ.'],
    ['Configure your API keys in Settings.', 'Cấu hình API key của bạn trong Cài đặt.'],
    ['The app will cache subtitles by video fingerprint.', 'Ứng dụng sẽ cache phụ đề theo video fingerprint.'],
    ['You won\'t be charged twice for the same video.', 'Bạn sẽ không bị tính phí hai lần cho cùng một video.'],
    ['Subtitles can be exported as .srt or .vtt files.', 'Phụ đề có thể xuất ra dưới dạng .srt hoặc .vtt.'],
    ['The transcript is fully interactive.', 'Bản ghi là hoàn toàn tương tác.'],
    ['Seek precisely by clicking any cue.', 'Tua chính xác bằng cách nhấp vào bất kỳ cue nào.'],
    ['This mock fixture demonstrates 50+ cues loading.', 'Fixture mock này minh họa tải hơn 50 cues.'],
    ['The composable useTranscript handles cue detection.', 'Composable useTranscript xử lý phát hiện cue.'],
    ['TDD tests cover boundary conditions and reactivity.', 'TDD tests bao phủ điều kiện biên và tính phản ứng.'],
    ['New providers can be added to the registry.', 'Các provider mới có thể được thêm vào registry.'],
    ['The provider abstraction ensures loose coupling.', 'Trừu tượng hóa provider đảm bảo kết nối lỏng.'],
    ['This architecture supports future extensions easily.', 'Kiến trúc này hỗ trợ mở rộng trong tương lai dễ dàng.'],
    ['TypeScript ensures type safety across the entire frontend.', 'TypeScript đảm bảo an toàn kiểu trên toàn bộ frontend.'],
    ['Pydantic models enforce types on the Python backend.', 'Pydantic models thực thi kiểu trên Python backend.'],
    ['The desktop runs as a native window via pywebview.', 'Ứng dụng desktop chạy như cửa sổ native qua pywebview.'],
    ['Video streaming uses HTTP range requests.', 'Phát video sử dụng HTTP range requests.'],
    ['Large video files are streamed efficiently.', 'Các tệp video lớn được phát trực tuyến hiệu quả.'],
    ['The bilingual display helps language learners.', 'Màn hình song ngữ giúp người học ngôn ngữ.'],
    ['Original subtitles appear on top, translations below.', 'Phụ đề gốc xuất hiện ở trên, bản dịch ở dưới.'],
    ['End-exclusive cue boundaries prevent overlap.', 'Ranh giới cue cuối độc quyền ngăn chặn chồng chéo.'],
    ['The gear icon opens the settings panel.', 'Biểu tượng bánh răng mở bảng cài đặt.'],
    ['Settings are persisted across restarts.', 'Cài đặt được lưu trữ qua các lần khởi động lại.'],
    ['A test connection button validates your API keys.', 'Nút kiểm tra kết nối xác thực API key của bạn.'],
    ['Video fingerprinting uses content hashing.', 'Video fingerprinting sử dụng content hashing.'],
    ['The subtitle cache avoids duplicate API calls.', 'Subtitle cache tránh các lần gọi API trùng lặp.'],
    ['Audio is extracted locally before sending to Deepgram.', 'Âm thanh được trích xuất cục bộ trước khi gửi đến Deepgram.'],
    ['Only the audio track is transmitted externally.', 'Chỉ có audio track được truyền ra ngoài.'],
    ['This preserves video privacy.', 'Điều này bảo vệ quyền riêng tư video.'],
    ['Each cue has a unique ID, start and end time.', 'Mỗi cue có ID duy nhất, thời gian bắt đầu và kết thúc.'],
    ['Cue IDs enable stable reference across sessions.', 'ID cue cho phép tham chiếu ổn định qua các phiên.'],
    ['The interactive footer scrolls horizontally.', 'Thanh footer tương tác cuộn theo chiều ngang.'],
    ['Active cue auto-scrolls into view smoothly.', 'Cue đang phát tự động cuộn mượt vào tầm nhìn.'],
    ['The transcript is read-only during playback.', 'Bản ghi chỉ đọc trong khi phát.'],
    ['Click-to-seek is the primary navigation gesture.', 'Click-to-seek là thao tác điều hướng chính.'],
    ['The app targets non-technical video consumers.', 'Ứng dụng nhắm đến người tiêu thụ video không chuyên kỹ thuật.'],
    ['A clean UI reduces cognitive load.', 'Giao diện sạch giảm tải nhận thức.'],
    ['Dark theme reduces eye strain during long sessions.', 'Chủ đề tối giảm mỏi mắt trong các phiên dài.'],
    ['Glassmorphism cards give a premium feel.', 'Thẻ glassmorphism mang lại cảm giác cao cấp.'],
    ['Indigo accent color ties the design together.', 'Màu accent indigo liên kết thiết kế lại.'],
    ['This is cue number 49 of 50 mock cues.', 'Đây là cue số 49 trong 50 mock cues.'],
    ['End of mock fixture demonstration.', 'Kết thúc bản demo mock fixture.'],
  ];

  cues.value = lines.map((pair, i) => ({
    id: String(i + 1),
    start: i * 4,
    end: (i + 1) * 4,
    originalText: pair[0],
    translatedText: pair[1],
  }));
}

// ── Settings state ───────────────────────────────────────────────────────────

const settingsOpen = ref<boolean>(false);
const settings = ref<AppSettings>({
  deepgram_api_key: '',
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

async function handleOpenVideo(): Promise<void> {
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
    const res: VideoDialogResponse = await window.pywebview.api.open_video_dialog();
    if (!res.cancelled && res.stream_url && res.filename) {
      videoSrc.value = res.stream_url;
      currentFilename.value = res.filename;
      loadMockCues();
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
        loadMockCues();
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

function handleSeek(time: number): void {
  // VideoPlayer exposes a seek method via template ref in a future issue.
  // For now emit through currentTime — VideoPlayer will handle seek in Issue 05.
  currentTime.value = time;
}

onMounted(() => {
  checkBackendBridge();
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
      @open-video="handleOpenVideo"
      @ping-backend="handlePingBackend"
      @open-settings="settingsOpen = true"
    />

    <!-- Main Workspace -->
    <main class="studio-workspace">
      <!-- Player Area -->
      <section class="player-wrapper">
        <VideoPlayer
          :src="videoSrc"
          :filename="currentFilename"
          @timeupdate="t => currentTime = t"
          @durationchange="d => duration = d"
          @open-file="handleOpenVideo"
        />
      </section>

      <!-- Interactive Transcript Footer -->
      <TranscriptFooter
        :cues="cues"
        :current-time="currentTime"
        @seek="handleSeek"
      />
    </main>

    <!-- Settings Modal -->
    <SettingsModal
      v-model="settingsOpen"
      :initial-settings="settings"
      @saved="handleSettingsSaved"
    />
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

.drag-icon {
  color: #38bdf8;
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.8; }
}
</style>
