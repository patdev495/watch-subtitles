<script setup lang="ts">
import { Activity, ArrowRight, FileVideo, FolderOpen, Languages, ListVideo, Loader2, Settings, Sparkles } from 'lucide-vue-next';
import { SUPPORTED_LANGUAGES, SUPPORTED_SOURCE_LANGUAGES } from '../languages';

const props = withDefaults(defineProps<{
  currentFilename?: string; backendConnected: boolean; isGenerating?: boolean; generationProgress?: number; hasSubtitles?: boolean; sourceLanguage?: string; targetLanguage?: string;
}>(), { currentFilename: '', isGenerating: false, generationProgress: 0, hasSubtitles: false, sourceLanguage: 'en', targetLanguage: 'vi' });
const emit = defineEmits<{
  (e: 'open-video'): void; (e: 'ping-backend'): void; (e: 'open-settings'): void;
  (e: 'update:sourceLanguage', lang: string): void; (e: 'update:targetLanguage', lang: string): void;
  (e: 'generate-subtitles', sourceLanguage: string, targetLanguage: string, force: boolean): void; (e: 'open-queue'): void;
}>();
const sourceLanguages = SUPPORTED_SOURCE_LANGUAGES;
const targetLanguages = SUPPORTED_LANGUAGES;
function updateLanguage(event: Event, kind: 'source' | 'target'): void {
  const value = (event.target as HTMLSelectElement).value;
  if (kind === 'source') emit('update:sourceLanguage', value);
  else emit('update:targetLanguage', value);
}
</script>

<template>
  <header class="header-bar">
    <div class="media-context" :title="currentFilename || 'Chưa chọn video'">
      <div class="media-icon"><FileVideo :size="17" aria-hidden="true" /></div>
      <div class="media-copy">
        <strong>{{ currentFilename || 'Chưa chọn video' }}</strong>
        <span>{{ hasSubtitles ? 'Đã có phụ đề' : 'Chưa có phụ đề' }}</span>
      </div>
    </div>

    <div class="language-control" aria-label="Cặp ngôn ngữ">
      <Languages :size="15" aria-hidden="true" />
      <label class="sr-only" for="source-language">Ngôn ngữ nguồn</label>
      <select id="source-language" :value="sourceLanguage" :disabled="isGenerating" @change="updateLanguage($event, 'source')"><option v-for="language in sourceLanguages" :key="language.code" :value="language.code">{{ language.name }}</option></select>
      <ArrowRight :size="14" aria-hidden="true" />
      <label class="sr-only" for="target-language">Ngôn ngữ đích</label>
      <select id="target-language" :value="targetLanguage" :disabled="isGenerating" @change="updateLanguage($event, 'target')"><option v-for="language in targetLanguages" :key="language.code" :value="language.code">{{ language.name }}</option></select>
    </div>

    <div class="main-actions">
      <button class="queue-button" title="Mở hàng đợi tạo phụ đề" @click="emit('open-queue')"><ListVideo :size="17" aria-hidden="true" /><span>Hàng đợi</span></button>
      <button class="generate-button" :disabled="!currentFilename || isGenerating" @click="emit('generate-subtitles', sourceLanguage, targetLanguage, hasSubtitles)">
        <Loader2 v-if="isGenerating" :size="17" class="spin" aria-hidden="true" /><Sparkles v-else :size="17" aria-hidden="true" />
        <span>{{ isGenerating ? `Đang tạo · ${Math.round(generationProgress)}%` : hasSubtitles ? 'Tạo lại' : 'Tạo phụ đề' }}</span>
      </button>
      <button class="open-button" :disabled="isGenerating" @click="emit('open-video')"><FolderOpen :size="17" aria-hidden="true" /><span>Mở video</span></button>
    </div>

    <div class="utility-actions">
      <button class="icon-button" title="Cài đặt API" aria-label="Cài đặt API" @click="emit('open-settings')"><Settings :size="18" aria-hidden="true" /></button>
      <button class="icon-button" title="Kiểm tra backend" aria-label="Kiểm tra backend" @click="emit('ping-backend')"><Activity :size="18" aria-hidden="true" /></button>
      <div class="engine-status" :class="{ active: backendConnected }" :title="backendConnected ? 'Backend đã sẵn sàng' : 'Đang kết nối backend'">
        <i aria-hidden="true" /><span>{{ backendConnected ? 'Sẵn sàng' : 'Kết nối' }}</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-bar { display: grid; grid-template-columns: minmax(170px, 1fr) auto auto auto; align-items: center; gap: 12px; min-height: 66px; padding: 10px clamp(16px, 2vw, 34px); background: rgba(7, 12, 23, .92); border-bottom: 1px solid rgba(148, 163, 184, .12); box-shadow: 0 8px 28px rgba(0, 0, 0, .22); user-select: none; z-index: 50; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; }.media-context { display: flex; align-items: center; min-width: 0; gap: 10px; }.media-icon { display: grid; place-items: center; width: 36px; height: 36px; flex: 0 0 36px; border: 1px solid rgba(96, 165, 250, .26); border-radius: 10px; color: #93c5fd; background: rgba(30, 64, 175, .2); }.media-copy { display: grid; min-width: 0; gap: 2px; }.media-copy strong { overflow: hidden; color: #e2e8f0; font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }.media-copy span { color: #64748b; font-size: 11px; }.media-copy span::before { content: '●'; margin-right: 5px; color: #10b981; }
.language-control, .main-actions, .utility-actions { display: flex; align-items: center; gap: 7px; }.language-control { height: 38px; padding: 0 9px; border: 1px solid rgba(148, 163, 184, .16); border-radius: 10px; color: #818cf8; background: rgba(30, 41, 59, .55); }.language-control select { max-width: 104px; border: 0; color: #e2e8f0; background: transparent; font: 650 12px var(--font-sans); outline: none; cursor: pointer; }.language-control select:disabled { cursor: not-allowed; opacity: .45; }.language-control option { color: #e2e8f0; background: #0f172a; }
button { display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-height: 38px; border: 1px solid transparent; border-radius: 10px; padding: 0 12px; color: #dbeafe; font: 700 13px var(--font-sans); cursor: pointer; transition: background .18s ease, border-color .18s ease, transform .18s ease; } button:hover:not(:disabled) { transform: translateY(-1px); } button:disabled { cursor: not-allowed; opacity: .45; }.queue-button { background: transparent; border-color: rgba(148, 163, 184, .18); }.queue-button:hover { border-color: rgba(129, 140, 248, .5); background: rgba(30, 41, 59, .75); }.generate-button { color: #fff; background: linear-gradient(135deg, #059669, #06b6d4); box-shadow: 0 7px 18px rgba(6, 182, 212, .18); }.open-button { color: #fff; background: linear-gradient(135deg, #4f46e5, #3b82f6); box-shadow: 0 7px 18px rgba(59, 130, 246, .18); }.icon-button { width: 38px; padding: 0; color: #94a3b8; background: transparent; border-color: rgba(148, 163, 184, .16); }.icon-button:hover { color: #c4b5fd; background: rgba(30, 41, 59, .7); }.engine-status { display: inline-flex; align-items: center; gap: 6px; padding: 0 10px; min-height: 30px; border: 1px solid rgba(148, 163, 184, .16); border-radius: 999px; color: #64748b; font-size: 11px; font-weight: 700; }.engine-status i { width: 7px; height: 7px; border-radius: 50%; background: #64748b; }.engine-status.active { color: #6ee7b7; border-color: rgba(16, 185, 129, .3); }.engine-status.active i { background: #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, .8); }.spin { animation: spin 1s linear infinite; } @keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 1050px) { .header-bar { grid-template-columns: minmax(150px, 1fr) auto auto; }.utility-actions { display: none; } } @media (max-width: 760px) { .header-bar { grid-template-columns: 1fr auto; }.language-control { grid-row: 2; grid-column: 1 / -1; }.main-actions span { display: none; }.main-actions button { width: 38px; padding: 0; } }
</style>
