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
      <FileVideo :size="16" :stroke-width="1.5" aria-hidden="true" />
      <div><strong>{{ currentFilename || 'Chưa chọn video' }}</strong><span>{{ hasSubtitles ? 'Đã có phụ đề' : 'Chưa có phụ đề' }}</span></div>
    </div>
    <div class="header-actions">
      <button class="ghost-button subtitle-button" aria-label="Phụ đề" title="Phụ đề" @click="emit('open-subtitles')"><Subtitles :size="16" :stroke-width="1.5" aria-hidden="true" /> Phụ đề</button>
      <button class="primary-button open-button" @click="emit('open-video')"><FolderOpen :size="16" :stroke-width="1.5" aria-hidden="true" /> Mở video</button>
      <button class="icon-button" aria-label="Cài đặt API" title="Cài đặt" @click="emit('open-settings')"><Settings :size="18" :stroke-width="1.5" aria-hidden="true" /></button>
      <button class="status-button" :class="{ ready: backendConnected }" :title="backendConnected ? 'Kiểm tra backend' : 'Kết nối · Kiểm tra backend'" @click="emit('ping-backend')"><Activity :size="16" :stroke-width="1.5" class="status-icon" aria-hidden="true" /><span class="status-dot" aria-hidden="true"></span>{{ backendConnected ? 'Sẵn sàng' : 'Kết nối' }}</button>
    </div>
  </header>
</template>

<style scoped>
.header-bar { height: var(--header-height); flex: 0 0 var(--header-height); display: flex; align-items: center; gap: var(--space-4); padding: 0 var(--space-4); background: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); }
.media-context { min-width: 0; flex: 1; display: flex; align-items: center; gap: var(--space-2); color: var(--text-secondary); }
.media-context > div { min-width: 0; display: flex; flex-direction: column; line-height: 1.15; }
.media-context strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-primary); font-size: var(--font-file); font-weight: 500; }
.media-context span { color: var(--text-muted); font-size: var(--font-meta); }
.header-actions { display: flex; align-items: center; gap: var(--space-2); }
button { height: var(--control-height); display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2); padding: 0 var(--space-3); border: 0; border-radius: var(--radius-control); background: transparent; color: var(--text-secondary); cursor: pointer; font-size: var(--font-body); font-weight: 500; white-space: nowrap; }
.ghost-button:hover, .icon-button:hover, .status-button:hover { background: var(--bg-hover); color: var(--text-primary); }
.primary-button { background: var(--accent-primary); color: var(--accent-contrast); }
.primary-button:hover { opacity: .88; }
.icon-button { width: var(--control-height); padding: 0; }
.status-button { font-size: var(--font-meta); }
.status-dot { width: var(--space-2); height: var(--space-2); border-radius: 50%; background: var(--text-muted); }
.ready .status-dot { background: var(--success); }
.status-icon { display: none; }
@media (max-width: 900px) { .header-bar { gap: var(--space-2); padding: 0 var(--space-3); } .status-button { padding: 0 var(--space-1); } }
</style>
