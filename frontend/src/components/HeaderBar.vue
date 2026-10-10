<script setup lang="ts">
import { Activity, FileVideo, FolderOpen, Settings, Sparkles } from 'lucide-vue-next';

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
      <FileVideo :size="18" aria-hidden="true" />
      <div><strong>{{ currentFilename || 'Chưa chọn video' }}</strong><span>{{ hasSubtitles ? 'Đã có phụ đề' : 'Chưa có phụ đề' }}</span></div>
    </div>
    <div class="main-actions">
      <button class="subtitle-button" aria-label="Phụ đề" @click="emit('open-subtitles')"><Sparkles :size="17" aria-hidden="true" /> Phụ đề</button>
      <button class="open-button" @click="emit('open-video')"><FolderOpen :size="17" aria-hidden="true" /> Mở video</button>
    </div>
    <div class="utility-actions">
      <button aria-label="Cài đặt API" @click="emit('open-settings')"><Settings :size="18" aria-hidden="true" /></button>
      <button aria-label="Kiểm tra backend" @click="emit('ping-backend')"><Activity :size="18" aria-hidden="true" /></button>
      <span class="engine-status">{{ backendConnected ? 'Sẵn sàng' : 'Kết nối' }}</span>
    </div>
  </header>
</template>

<style scoped>
.header-bar { display: flex; align-items: center; gap: 16px; min-height: 66px; padding: 10px clamp(16px, 2vw, 34px); background: var(--bg-surface); border-bottom: 1px solid var(--border-subtle); color: var(--text-primary); }
.media-context { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; color: var(--text-secondary); }
.media-context div { display: grid; gap: 2px; min-width: 0; }
.media-context strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-primary); font-size: 13px; font-weight: 600; }
.media-context span { font-size: 11px; color: var(--text-muted); }
.main-actions, .utility-actions { display: flex; align-items: center; gap: 7px; }
button { display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-height: var(--control-height); padding: 0 12px; border: 1px solid var(--border-strong); border-radius: var(--radius-control); color: var(--text-primary); background: var(--bg-control); cursor: pointer; font: 600 12px var(--font-sans); white-space: nowrap; }
button:hover { background: var(--bg-raised); border-color: var(--text-muted); }
.subtitle-button { background: var(--accent-soft); border-color: var(--accent-primary); color: var(--accent-hover); }
.subtitle-button:hover { background: var(--accent-primary); border-color: var(--accent-primary); color: var(--accent-contrast); }
.open-button { color: var(--accent-contrast); background: var(--accent-primary); border-color: var(--accent-primary); }
.open-button:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
.utility-actions button { width: var(--control-height); padding: 0; }
.engine-status { color: var(--text-muted); font-size: 11px; }
@media (max-width: 700px) { .header-bar { flex-wrap: wrap; }.utility-actions { display: none; } }
</style>
