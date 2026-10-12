<script setup lang="ts">
import { computed } from 'vue';
import { Activity, Clapperboard, FileVideo, FolderOpen, Moon, Settings, Subtitles, Sun } from 'lucide-vue-next';
import { useTheme } from '../composables/useTheme';

withDefaults(defineProps<{ currentFilename?: string; backendConnected: boolean; hasSubtitles?: boolean }>(), {
  currentFilename: '', hasSubtitles: false,
});
const emit = defineEmits<{
  (event: 'open-video'): void;
  (event: 'ping-backend'): void;
  (event: 'open-settings'): void;
  (event: 'open-subtitles'): void;
}>();

const { theme, toggleTheme } = useTheme();
const themeLabel = computed(() => (theme.value === 'dark' ? 'Chuyển giao diện sáng' : 'Chuyển giao diện tối'));
</script>

<template>
  <header class="header-bar">
    <div class="brand">
      <span class="brand-mark" aria-hidden="true"><Clapperboard :size="17" :stroke-width="2" /></span>
      <span class="brand-name">Watch Subtitles</span>
    </div>

    <span class="header-divider" aria-hidden="true"></span>

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
      <button
        class="status-button"
        :class="{ ready: backendConnected }"
        :title="backendConnected ? 'Kiểm tra backend' : 'Kết nối · Kiểm tra backend'"
        :aria-label="backendConnected ? 'Kiểm tra backend' : 'Kết nối · Kiểm tra backend'"
        @click="emit('ping-backend')"
      >
        <Activity :size="15" :stroke-width="1.75" class="status-icon" aria-hidden="true" />
        <span class="status-dot" aria-hidden="true"></span>
      </button>
      <button class="icon-button" :title="themeLabel" :aria-label="themeLabel" @click="toggleTheme">
        <Sun v-if="theme === 'dark'" :size="17" :stroke-width="1.75" aria-hidden="true" />
        <Moon v-else :size="17" :stroke-width="1.75" aria-hidden="true" />
      </button>
      <button class="icon-button" aria-label="Cài đặt API" title="Cài đặt" @click="emit('open-settings')">
        <Settings :size="17" :stroke-width="1.75" aria-hidden="true" />
      </button>
      <button class="ghost-button subtitle-button" aria-label="Phụ đề" title="Phụ đề" @click="emit('open-subtitles')">
        <Subtitles :size="16" :stroke-width="1.75" aria-hidden="true" />
        <span>Phụ đề</span>
      </button>
      <button class="primary-button open-button" @click="emit('open-video')">
        <FolderOpen :size="16" :stroke-width="2" aria-hidden="true" />
        <span>Mở video</span>
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
  gap: var(--space-4);
  padding: 0 var(--space-4);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  user-select: none;
  z-index: 100;
}

/* ── Brand ──────────────────────────────────────────────────────────────── */
.brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
}

.brand-name {
  color: var(--text-primary);
  font-size: var(--font-body);
  font-weight: 600;
  white-space: nowrap;
}

.header-divider {
  width: 1px;
  height: 22px;
  background: var(--border-subtle);
  flex-shrink: 0;
}

/* ── Current Video ──────────────────────────────────────────────────────── */
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
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--bg-raised);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  flex-shrink: 0;
}

.media-details {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
  line-height: 1.25;
}

.media-details strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
  font-size: var(--font-file);
  font-weight: 600;
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
  box-shadow: 0 0 0 3px var(--success-soft);
}

/* ── Actions ────────────────────────────────────────────────────────────── */
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
  background: var(--bg-raised);
  color: var(--text-primary);
}

.ghost-button:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
}

.primary-button {
  background: var(--accent);
  color: var(--accent-contrast);
  border-color: var(--accent);
  font-weight: 600;
  padding: 0 var(--space-4);
  box-shadow: 0 6px 18px -10px color-mix(in srgb, var(--accent) 90%, transparent);
}

.primary-button:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

.primary-button:active {
  background: var(--accent-active);
  border-color: var(--accent-active);
}

.icon-button {
  width: var(--control-height);
  padding: 0;
  border-color: var(--border-subtle);
  background: var(--bg-raised);
}

.icon-button:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.status-button {
  width: var(--control-height);
  padding: 0;
  border-color: var(--border-subtle);
  background: var(--bg-raised);
}

.status-button:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}

.ready .status-dot {
  background: var(--success);
  box-shadow: 0 0 0 3px var(--success-soft);
}

.status-icon {
  display: none;
}

@media (max-width: 1080px) {
  .brand-name {
    display: none;
  }
}

@media (max-width: 900px) {
  .header-bar {
    gap: var(--space-2);
    padding: 0 var(--space-3);
  }
  .subtitle-button span {
    display: none;
  }
}
</style>
