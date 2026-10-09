<script setup lang="ts">
import { FolderOpen, Film, Activity, Sparkles, Settings, Languages, Loader2 } from 'lucide-vue-next';

const props = withDefaults(
  defineProps<{
    currentFilename?: string;
    backendConnected: boolean;
    isGenerating?: boolean;
    hasSubtitles?: boolean;
    sourceLanguage?: string;
    targetLanguage?: string;
  }>(),
  {
    currentFilename: '',
    isGenerating: false,
    hasSubtitles: false,
    sourceLanguage: 'en',
    targetLanguage: 'vi',
  }
);

const emit = defineEmits<{
  (e: 'open-video'): void;
  (e: 'ping-backend'): void;
  (e: 'open-settings'): void;
  (e: 'update:sourceLanguage', lang: string): void;
  (e: 'update:targetLanguage', lang: string): void;
  (e: 'generate-subtitles', sourceLanguage: string, targetLanguage: string): void;
}>();

const languages = [
  { code: 'vi', name: 'Tiếng Việt' },
  { code: 'en', name: 'English' },
  { code: 'ja', name: '日本語' },
  { code: 'zh-CN', name: '中文（简体）' },
  { code: 'zh-TW', name: '中文（繁體）' },
  { code: 'fr', name: 'Français' },
  { code: 'es', name: 'Español' },
  { code: 'de', name: 'Deutsch' },
];

function updateLanguage(event: Event, kind: 'source' | 'target'): void {
  const target = event.target as HTMLSelectElement;
  if (kind === 'source') {
    emit('update:sourceLanguage', target.value);
  } else {
    emit('update:targetLanguage', target.value);
  }
}
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
        <span v-if="hasSubtitles" class="subtitle-available" role="status" aria-atomic="true">Đã có phụ đề</span>
      </div>
      <div v-else class="empty-state-badge">
        <span>Chưa chọn video</span>
      </div>
    </div>

    <!-- Right Actions -->
    <div class="actions-group">
      <div class="lang-selector-wrapper" title="Chọn ngôn ngữ gốc của video">
        <Languages :size="14" class="lang-icon" />
        <select
          class="lang-select"
          :value="sourceLanguage"
          :disabled="isGenerating"
          aria-label="Ngôn ngữ gốc"
          @change="updateLanguage($event, 'source')"
        >
          <option disabled value="">Ngôn ngữ gốc</option>
          <option v-for="lang in languages" :key="lang.code" :value="lang.code">
            {{ lang.name }}
          </option>
        </select>
      </div>

      <div class="lang-selector-wrapper" title="Chọn ngôn ngữ dịch phụ đề">
        <Languages :size="14" class="lang-icon" />
        <select
          class="lang-select"
          :value="targetLanguage"
          :disabled="isGenerating"
          aria-label="Ngôn ngữ đích"
          @change="updateLanguage($event, 'target')"
        >
          <option disabled value="">Ngôn ngữ đích</option>
          <option v-for="lang in languages" :key="lang.code" :value="lang.code">
            {{ lang.name }}
          </option>
        </select>
      </div>

      <!-- Generate Subtitles Button -->
      <button
        class="action-btn generate-btn"
        :class="{ running: isGenerating }"
        :disabled="!currentFilename || isGenerating"
        :title="!currentFilename ? 'Hãy mở video trước khi tạo phụ đề' : 'Bắt đầu quy trình tự động STT & dịch thuật'"
        @click="emit('generate-subtitles', sourceLanguage, targetLanguage)"
      >
        <Loader2 v-if="isGenerating" :size="15" class="btn-icon spin" />
        <Sparkles v-else :size="15" class="btn-icon" />
        <span>{{ isGenerating ? 'Đang tạo...' : hasSubtitles ? 'Tạo lại phụ đề' : 'Tạo phụ đề' }}</span>
      </button>

      <!-- Open Video Primary Button -->
      <button
        class="action-btn primary"
        title="Chọn video từ máy tính"
        :disabled="isGenerating"
        @click="emit('open-video')"
      >
        <FolderOpen :size="15" class="btn-icon" />
        <span>Mở Video</span>
      </button>

      <!-- Settings Button -->
      <button
        class="icon-btn-settings"
        title="Cài đặt API"
        @click="emit('open-settings')"
      >
        <Settings :size="15" />
      </button>

      <!-- Bridge Ping Test -->
      <button
        class="action-btn secondary"
        title="Kiểm tra kết nối Python backend bridge"
        @click="emit('ping-backend')"
      >
        <Activity :size="14" class="btn-icon" />
        <span>Bridge</span>
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

.subtitle-available {
  flex-shrink: 0;
  padding: 3px 7px;
  border: 1px solid rgba(52, 211, 153, 0.45);
  border-radius: 999px;
  color: #6ee7b7;
  background: rgba(6, 78, 59, 0.5);
  font-size: 10px;
  font-weight: 700;
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

.action-btn.generate-btn {
  background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
}

.action-btn.generate-btn:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
  filter: brightness(1.1);
}

.action-btn.generate-btn:disabled,
.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.lang-selector-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 0 10px;
  height: 32px;
}

.lang-icon {
  color: #818cf8;
  flex-shrink: 0;
}

.lang-select {
  background: transparent;
  border: none;
  color: #e2e8f0;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  outline: none;
}

.lang-select option {
  background: #0f172a;
  color: #e2e8f0;
}

.spin {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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

.icon-btn-settings {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(30, 41, 59, 0.6);
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.icon-btn-settings:hover {
  background: rgba(99, 102, 241, 0.12);
  color: #818cf8;
  border-color: rgba(99, 102, 241, 0.3);
}
</style>
