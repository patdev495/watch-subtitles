<script setup lang="ts">
import { FolderOpen, Film, Activity, Sparkles } from 'lucide-vue-next';

defineProps<{
  currentFilename?: string;
  backendConnected: boolean;
}>();

const emit = defineEmits<{
  (e: 'open-video'): void;
  (e: 'ping-backend'): void;
}>();
</script>

<template>
  <header class="header-bar">
    <!-- Brand / Logo -->
    <div class="logo-group">
      <div class="logo-badge">
        <Film :size="18" class="logo-icon" />
      </div>
      <div class="brand-text">
        <span class="app-title">Watch Subtitles</span>
        <span class="badge">STUDIO</span>
      </div>
    </div>

    <!-- Active Media Status Indicator -->
    <div class="middle-info">
      <div v-if="currentFilename" class="active-file-pill">
        <Sparkles :size="13" class="file-icon" />
        <span class="active-filename" :title="currentFilename">{{ currentFilename }}</span>
      </div>
      <div v-else class="empty-state-badge">
        <span>Chưa chọn video</span>
      </div>
    </div>

    <!-- Right Actions -->
    <div class="actions-group">
      <!-- Bridge Ping Test -->
      <button
        class="action-btn secondary"
        title="Kiểm tra kết nối Python backend bridge"
        @click="emit('ping-backend')"
      >
        <Activity :size="14" class="btn-icon" />
        <span>Bridge</span>
      </button>

      <!-- Open Video Primary Button -->
      <button
        class="action-btn primary"
        title="Chọn video từ máy tính"
        @click="emit('open-video')"
      >
        <FolderOpen :size="15" class="btn-icon" />
        <span>Mở Video</span>
      </button>

      <!-- Status Pill -->
      <div
        class="status-pill"
        :class="{ active: backendConnected }"
        :title="backendConnected ? 'Python UV Backend kết nối thành công' : 'Đang kết nối backend...'"
      >
        <span class="status-dot"></span>
        <span class="status-text">{{ backendConnected ? 'Engine Ready' : 'Connecting' }}</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: rgba(11, 15, 25, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  user-select: none;
  z-index: 50;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-badge {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px rgba(99, 102, 241, 0.4);
}

.logo-icon {
  color: #ffffff;
}

.brand-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-title {
  font-weight: 700;
  font-size: 15px;
  letter-spacing: -0.01em;
  background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 2px 7px;
  border-radius: 20px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #818cf8;
}

.middle-info {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 0 20px;
  overflow: hidden;
}

.active-file-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 9999px;
  padding: 5px 14px;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.1);
  max-width: 450px;
}

.file-icon {
  color: #38bdf8;
  flex-shrink: 0;
}

.active-filename {
  font-size: 12px;
  font-weight: 500;
  color: #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state-badge {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.actions-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 600;
  padding: 7px 15px;
  border-radius: 8px;
  cursor: pointer;
  border: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  user-select: none;
}

.action-btn:active {
  transform: scale(0.97);
}

.action-btn.primary {
  background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}

.action-btn.primary:hover {
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
  filter: brightness(1.1);
}

.action-btn.secondary {
  background: rgba(30, 41, 59, 0.6);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.action-btn.secondary:hover {
  background: rgba(51, 65, 85, 0.7);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.16);
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #64748b;
  transition: all 0.3s ease;
}

.status-pill.active {
  border-color: rgba(16, 185, 129, 0.3);
  color: #6ee7b7;
}

.status-pill.active .status-dot {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
}
</style>
