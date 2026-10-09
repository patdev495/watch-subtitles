<script setup lang="ts">
import { ref, onMounted } from 'vue';
import HeaderBar from './components/HeaderBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import { Subtitles, Sparkles } from 'lucide-vue-next';
import type { VideoDialogResponse } from './types';

const videoSrc = ref<string>('');
const currentFilename = ref<string>('');
const backendConnected = ref<boolean>(false);
const isDragging = ref<boolean>(false);

const currentTime = ref<number>(0);
const duration = ref<number>(0);

async function checkBackendBridge() {
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
        } catch (err) {
          console.error(err);
        }
      }
    });
  }
}

async function handleOpenVideo() {
  if (!window.pywebview?.api) {
    // If testing in standard web browser without pywebview
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'video/*';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        videoSrc.value = URL.createObjectURL(file);
        currentFilename.value = file.name;
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
    }
  } catch (err) {
    console.error('Lỗi khi mở video:', err);
  }
}

async function handlePingBackend() {
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

async function handleDrop(event: DragEvent) {
  isDragging.value = false;
  event.preventDefault();

  const files = event.dataTransfer?.files;
  if (!files || files.length === 0) return;

  const file = files[0];
  const anyFile = file as any;

  if (window.pywebview?.api && anyFile.path) {
    try {
      const res = await window.pywebview.api.load_video_path(anyFile.path);
      if (!res.cancelled && res.stream_url) {
        videoSrc.value = res.stream_url;
        currentFilename.value = res.filename || file.name;
        return;
      }
    } catch (err) {
      console.warn('Backend load path error, fallback to URL.createObjectURL', err);
    }
  }

  videoSrc.value = URL.createObjectURL(file);
  currentFilename.value = file.name;
}

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  isDragging.value = true;
}

function handleDragLeave() {
  isDragging.value = false;
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

      <!-- Footer: Interactive Transcript Preview Bar -->
      <footer class="transcript-tray">
        <div class="tray-left">
          <div class="tray-icon-box">
            <Subtitles :size="16" class="tray-icon" />
          </div>
          <div class="tray-text">
            <span class="tray-title">Phụ đề song ngữ (Interactive Transcript)</span>
            <span v-if="!videoSrc" class="tray-sub">Chưa có video được chọn. Tải video để bắt đầu.</span>
            <span v-else class="tray-sub active">Video đã sẵn sàng. Chuyển sang Issue 03 để kích hoạt bảng phụ đề tương tác.</span>
          </div>
        </div>

        <div class="tray-right">
          <span class="badge-stage">Phase 2: Local Playback Ready</span>
        </div>
      </footer>
    </main>
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

/* Transcript Footer Tray */
.transcript-tray {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(11, 15, 29, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  user-select: none;
}

.tray-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.tray-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.tray-icon {
  color: #818cf8;
}

.tray-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tray-title {
  font-size: 13px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.01em;
}

.tray-sub {
  font-size: 12px;
  color: #64748b;
}

.tray-sub.active {
  color: #38bdf8;
}

.badge-stage {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: #34d399;
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
