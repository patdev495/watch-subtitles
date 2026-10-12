<script setup lang="ts">
import { Activity, FileVideo, FolderOpen, Settings, Subtitles } from 'lucide-vue-next';

withDefaults(defineProps<{ currentFilename?: string; backendConnected: boolean; hasSubtitles?: boolean }>(), {
  currentFilename: '', hasSubtitles: false,
});
const emit = defineEmits<{
  (event: 'open-video'): void;
  (event: 'ping-backend'): void;
  (event: 'open-settings'): void;
  (event: 'open-subtitles'): void;
}>();
</script>

<template>
  <header class="header-bar">
    <div class="media-context" :title="currentFilename || 'Chưa chọn video'">
      <div class="media-icon-wrapper">
        <FileVideo :size="16" :stroke-width="1.75" aria-hidden="true" />
      </div>
      <div class="media-details">
        <strong>{{ currentFilename || 'Chưa chọn video' }}</strong>
        <span class="subtitle-status">
          <span class="status-indicator-dot" :class="{ 'has-subtitles': hasSubtitles }" aria-hidden="true"></span>
          {{ hasSubtitles ? 'Đã có phụ đề' : 'Chưa có phụ đề' }}
        </span>
      </div>
    </div>
    <div class="header-actions">
      <button class="ghost-button subtitle-button" aria-label="Phụ đề" title="Phụ đề" @click="emit('open-subtitles')">
        <Subtitles :size="15" :stroke-width="1.75" aria-hidden="true" />
        <span>Phụ đề</span>
      </button>
      <button class="primary-button open-button" @click="emit('open-video')">
        <FolderOpen :size="15" :stroke-width="1.75" aria-hidden="true" />
        <span>Mở video</span>
      </button>
      <button class="icon-button" aria-label="Cài đặt API" title="Cài đặt" @click="emit('open-settings')">
        <Settings :size="17" :stroke-width="1.75" aria-hidden="true" />
      </button>
      <button class="status-button" :class="{ ready: backendConnected }" :title="backendConnected ? 'Kiểm tra backend' : 'Kết nối · Kiểm tra backend'" @click="emit('ping-backend')">
        <Activity :size="15" :stroke-width="1.75" class="status-icon" aria-hidden="true" />
        <span class="status-dot" aria-hidden="true"></span>
        <span>{{ backendConnected ? 'Sẵn sàng' : 'Kết nối' }}</span>
      </button>
    </div>
  </header>
</template>

<style scoped>
.header-bar {
  height: var(--header-height);
  flex: 0 0 var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: 0 var(--space-4);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  backdrop-filter: var(--blur-glass);
  user-select: none;
  z-index: 100;
}

.media-context {
  min-width: 0;
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--text-secondary);
}

.media-icon-wrapper {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--bg-control);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  flex-shrink: 0;
}

.media-details {
  min-width: 0;
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.media-details strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
  font-size: var(--font-file);
  font-weight: 600;
  letter-spacing: -0.01em;
}

.subtitle-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--text-muted);
  font-size: var(--font-meta);
}

.status-indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  flex-shrink: 0;
}

.status-indicator-dot.has-subtitles {
  background: var(--success);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

button {
  height: var(--control-height);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: 0 var(--space-3);
  border: 1px solid transparent;
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--font-body);
  font-weight: 500;
  white-space: nowrap;
}

.ghost-button {
  border-color: var(--border-subtle);
  background: var(--bg-hover);
  color: var(--text-primary);
}

.ghost-button:hover {
  background: var(--bg-selected);
  border-color: var(--border-strong);
}

.primary-button {
  background: #ffffff;
  color: #09090b;
  border: 1px solid #ffffff;
  font-weight: 600;
}

.primary-button:hover {
  background: #e4e4e7;
  border-color: #e4e4e7;
}

.primary-button:active {
  background: #d4d4d8;
}

.icon-button {
  width: var(--control-height);
  padding: 0;
  border-color: var(--border-subtle);
  background: var(--bg-hover);
}

.icon-button:hover {
  background: var(--bg-selected);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.status-button {
  font-size: var(--font-meta);
  border-color: var(--border-subtle);
  background: var(--bg-hover);
  padding: 0 var(--space-2);
}

.status-button:hover {
  background: var(--bg-selected);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-muted);
}

.ready .status-dot {
  background: var(--success);
}

.status-icon {
  display: none;
}

@media (max-width: 900px) {
  .header-bar {
    gap: var(--space-2);
    padding: 0 var(--space-3);
  }
  .status-button {
    padding: 0 var(--space-1);
  }
}
</style>
