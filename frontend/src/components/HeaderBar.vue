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
.header-bar { display: flex; align-items: center; gap: 16px; min-height: 66px; padding: 10px clamp(16px, 2vw, 34px); background: #070c17; border-bottom: 1px solid #334155; color: #e2e8f0; }
.media-context { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; }.media-context div { display: grid; gap: 2px; min-width: 0; }.media-context strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }.media-context span { font-size: 11px; color: #94a3b8; }
.main-actions, .utility-actions { display: flex; align-items: center; gap: 7px; } button { display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-height: 38px; padding: 0 12px; border: 1px solid #475569; border-radius: 9px; color: #e2e8f0; background: #1e293b; cursor: pointer; font: 700 13px var(--font-sans); }.subtitle-button { color: #fff; background: #047857; border-color: #059669; }.open-button { color: #fff; background: #4338ca; border-color: #4f46e5; }.utility-actions button { width: 38px; padding: 0; }.engine-status { color: #94a3b8; font-size: 11px; }
@media (max-width: 700px) { .header-bar { flex-wrap: wrap; }.utility-actions { display: none; } }
</style>
