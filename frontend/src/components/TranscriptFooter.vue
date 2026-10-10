<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { Download, Eye, EyeOff, SlidersHorizontal, X } from 'lucide-vue-next';
import { pinyin } from 'pinyin-pro';
import type { Cue, SubtitleDisplayPreferences, SubtitleLine } from '../types';
import { useTranscript } from '../composables/useTranscript';

const props = defineProps<{
  cues: Cue[];
  currentTime: number;
  sourceLanguage: string;
  targetLanguage: string;
  isFullscreen?: boolean;
  controlsVisible?: boolean;
  preferences?: SubtitleDisplayPreferences;
}>();

const emit = defineEmits<{ (event: 'update:preferences', value: SubtitleDisplayPreferences): void }>();

const cuesRef = computed(() => props.cues);
const currentTimeRef = computed(() => props.currentTime);
const { activeCue } = useTranscript(cuesRef, currentTimeRef);
const primaryLine = ref<'original' | 'translated'>(props.preferences?.primary_line ?? 'translated');
const detailOpen = ref(false);
const settingsOpen = ref(false);
const subtitlesVisible = ref(props.preferences?.overlay_visible ?? true);
const chineseLanguage = (language: string): boolean => language.toLowerCase().startsWith('zh');
const originalPinyin = computed(() => activeCue.value && chineseLanguage(props.sourceLanguage)
  ? pinyin(activeCue.value.originalText, { toneType: 'symbol' }) : '');
const translatedPinyin = computed(() => activeCue.value && chineseLanguage(props.targetLanguage)
  ? pinyin(activeCue.value.translatedText, { toneType: 'symbol' }) : '');
const primaryText = computed(() => activeCue.value
  ? primaryLine.value === 'original' ? activeCue.value.originalText : activeCue.value.translatedText
  : '');
const secondaryLine = computed<'original' | 'translated'>(() => primaryLine.value === 'original' ? 'translated' : 'original');
const secondaryText = computed(() => activeCue.value
  ? secondaryLine.value === 'original' ? activeCue.value.originalText : activeCue.value.translatedText
  : '');

const lineSettings = reactive<Record<SubtitleLine, { visible: boolean; fontSize: number }>>({
  original: { visible: props.preferences?.lines.original.visible ?? true, fontSize: props.preferences?.lines.original.font_size ?? 20 },
  originalPinyin: { visible: props.preferences?.lines.originalPinyin.visible ?? true, fontSize: props.preferences?.lines.originalPinyin.font_size ?? 15 },
  translated: { visible: props.preferences?.lines.translated.visible ?? true, fontSize: props.preferences?.lines.translated.font_size ?? 18 },
  translatedPinyin: { visible: props.preferences?.lines.translatedPinyin.visible ?? true, fontSize: props.preferences?.lines.translatedPinyin.font_size ?? 15 },
});
function snapshotPreferences(): SubtitleDisplayPreferences {
  return {
    primary_line: primaryLine.value, overlay_visible: subtitlesVisible.value,
    lines: {
      original: { visible: lineSettings.original.visible, font_size: lineSettings.original.fontSize },
      originalPinyin: { visible: lineSettings.originalPinyin.visible, font_size: lineSettings.originalPinyin.fontSize },
      translated: { visible: lineSettings.translated.visible, font_size: lineSettings.translated.fontSize },
      translatedPinyin: { visible: lineSettings.translatedPinyin.visible, font_size: lineSettings.translatedPinyin.fontSize },
    },
  };
}
function notifyPreferences(): void { emit('update:preferences', snapshotPreferences()); }
watch(() => props.preferences, (preferences) => {
  if (!preferences) return;
  primaryLine.value = preferences.primary_line;
  subtitlesVisible.value = preferences.overlay_visible;
  for (const key of ['original', 'originalPinyin', 'translated', 'translatedPinyin'] as const) {
    lineSettings[key].visible = preferences.lines[key].visible;
    lineSettings[key].fontSize = preferences.lines[key].font_size;
  }
});
const detailLines = computed(() => [
  { key: 'original' as const, label: 'Gốc', text: activeCue.value?.originalText ?? '', minimum: 12 },
  ...(originalPinyin.value ? [{ key: 'originalPinyin' as const, label: 'Pinyin gốc', text: originalPinyin.value, minimum: 10 }] : []),
  { key: 'translated' as const, label: 'Dịch', text: activeCue.value?.translatedText ?? '', minimum: 12 },
  ...(translatedPinyin.value ? [{ key: 'translatedPinyin' as const, label: 'Pinyin dịch', text: translatedPinyin.value, minimum: 10 }] : []),
]);

function lineStyle(line: SubtitleLine): { fontSize: string } { return { fontSize: `${lineSettings[line].fontSize}px` }; }
function updateFontSize(line: SubtitleLine, event: Event): void { lineSettings[line].fontSize = Number((event.target as HTMLInputElement).value); notifyPreferences(); }
function choosePrimary(line: 'original' | 'translated'): void { primaryLine.value = line; notifyPreferences(); }
function toggleSubtitles(): void { subtitlesVisible.value = !subtitlesVisible.value; notifyPreferences(); }
function toggleLine(line: SubtitleLine): void { lineSettings[line].visible = !lineSettings[line].visible; notifyPreferences(); }
function closePanel(): void { detailOpen.value = false; settingsOpen.value = false; }
function toggleSettingsPanel(): void {
  if (settingsOpen.value) {
    closePanel();
    return;
  }
  detailOpen.value = true;
  settingsOpen.value = true;
}

const exportFormats = ['srt', 'vtt'] as const;
const exportLayouts = [{ value: 'bilingual', label: 'Song ngữ' }, { value: 'original', label: 'Chỉ gốc' }, { value: 'translated', label: 'Chỉ dịch' }] as const;
const selectedFmt = ref<'srt' | 'vtt'>('srt');
const selectedLayout = ref<'bilingual' | 'original' | 'translated'>('bilingual');
const exporting = ref(false);
const exportMessage = ref('');

function timestamp(seconds: number, separator: ',' | '.'): string {
  const milliseconds = Math.round(seconds * 1000);
  const hours = Math.floor(milliseconds / 3_600_000);
  const minutes = Math.floor((milliseconds % 3_600_000) / 60_000);
  const secs = Math.floor((milliseconds % 60_000) / 1_000);
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}${separator}${(milliseconds % 1_000).toString().padStart(3, '0')}`;
}
function exportText(cue: Cue): string {
  return selectedLayout.value === 'original' ? cue.originalText : selectedLayout.value === 'translated' ? cue.translatedText : `${cue.originalText}\n${cue.translatedText}`;
}
async function exportSubtitles(): Promise<void> {
  if (!props.cues.length) return;
  exporting.value = true;
  try {
    if (window.pywebview?.api) {
      const result = await window.pywebview.api.export_subtitles(props.cues, selectedFmt.value, selectedLayout.value);
      exportMessage.value = result.ok ? 'Đã lưu subtitle.' : result.error ?? 'Xuất thất bại.';
    } else {
      const separator = selectedFmt.value === 'srt' ? ',' : '.';
      const blocks = props.cues.map((cue, index) => `${index + 1}\n${timestamp(cue.start, separator)} --> ${timestamp(cue.end, separator)}\n${exportText(cue)}`);
      const content = selectedFmt.value === 'vtt' ? `WEBVTT\n\n${blocks.join('\n\n')}\n` : `${blocks.join('\n\n')}\n`;
      const link = document.createElement('a');
      link.href = URL.createObjectURL(new Blob([content], { type: 'text/plain;charset=utf-8' }));
      link.download = `subtitles.${selectedFmt.value}`;
      link.click();
      URL.revokeObjectURL(link.href);
      exportMessage.value = 'Đã tải subtitle.';
    }
  } catch (error) { exportMessage.value = `Xuất thất bại: ${String(error)}`; }
  finally { exporting.value = false; }
}
</script>

<template>
  <section v-if="activeCue" :class="['subtitle-overlay', { fullscreen: isFullscreen, 'controls-visible': controlsVisible, 'panel-open': detailOpen || settingsOpen }]" aria-label="Phụ đề hiện tại">
    <div class="subtitle-toolbar" aria-label="Điều khiển phụ đề">
      <button
        class="toolbar-button"
        :aria-label="subtitlesVisible ? 'Ẩn phụ đề' : 'Hiện phụ đề'"
        :aria-pressed="subtitlesVisible"
        @click="toggleSubtitles"
      >
        <Eye v-if="subtitlesVisible" :size="18" aria-hidden="true" />
        <EyeOff v-else :size="18" aria-hidden="true" />
        <span>Sub</span>
      </button>
      <button
        class="toolbar-button"
        aria-label="Mở chỉnh phụ đề"
        :aria-expanded="settingsOpen"
        @click="toggleSettingsPanel"
      >
        <SlidersHorizontal :size="18" aria-hidden="true" />
        <span>Aa</span>
      </button>
    </div>

    <div v-if="subtitlesVisible && lineSettings[primaryLine].visible" class="caption-card" :style="lineStyle(primaryLine)" title="Nhấp để xem chi tiết phụ đề" role="button" tabindex="0" aria-label="Mở chi tiết phụ đề" @click="detailOpen = true" @keydown.enter="detailOpen = true" @keydown.space.prevent="detailOpen = true">
      <span v-if="lineSettings[secondaryLine].visible" :class="secondaryLine === 'original' ? 'caption-original' : 'caption-translation'">{{ secondaryText }}</span>
      <span class="caption-text" :class="primaryLine === 'original' ? 'caption-original' : 'caption-translation'">{{ primaryText }}</span>
    </div>

    <aside v-if="detailOpen || settingsOpen" class="cue-drawer" :aria-label="detailOpen ? 'Chi tiết phụ đề hiện tại' : 'Chỉnh hiển thị phụ đề'">
      <div class="drawer-header">
        <strong>{{ detailOpen ? 'Chi tiết câu hiện tại' : 'Chỉnh hiển thị' }}</strong>
        <button class="icon-button" aria-label="Đóng bảng phụ đề" @click="closePanel"><X :size="16" aria-hidden="true" /></button>
      </div>
      <div v-if="detailOpen || settingsOpen" class="primary-switch" aria-label="Dòng sub trên video">
        <button :class="{ selected: primaryLine === 'original' }" :aria-pressed="primaryLine === 'original'" aria-label="Hiển thị dòng gốc trên video" @click="choosePrimary('original')">Gốc</button>
        <button :class="{ selected: primaryLine === 'translated' }" :aria-pressed="primaryLine === 'translated'" aria-label="Hiển thị dòng dịch trên video" @click="choosePrimary('translated')">Dịch</button>
      </div>
      <div v-for="line in detailOpen ? detailLines : []" :key="line.key" v-show="lineSettings[line.key].visible" class="detail-line" :class="`detail-line--${line.key}`">
        <span>{{ line.label }}</span>
        <p class="selectable-detail-text" :style="lineStyle(line.key)" @pointerdown.stop @mousedown.stop>{{ line.text }}</p>
      </div>
      <div v-if="settingsOpen" class="display-settings">
        <strong>Hiển thị &amp; cỡ chữ</strong>
        <div v-for="line in detailLines" :key="line.key" class="setting-row">
          <button class="icon-button" :aria-label="`${lineSettings[line.key].visible ? 'Ẩn' : 'Hiện'} dòng ${line.label}`" @click="toggleLine(line.key)">
            <Eye v-if="lineSettings[line.key].visible" :size="16" aria-hidden="true" /><EyeOff v-else :size="16" aria-hidden="true" />
          </button>
          <label :for="`font-${line.key}`">{{ line.label }}</label>
          <input :id="`font-${line.key}`" :aria-label="`Cỡ chữ dòng ${line.label}`" type="range" :min="line.minimum" max="36" :value="lineSettings[line.key].fontSize" @input="updateFontSize(line.key, $event)">
          <output>{{ lineSettings[line.key].fontSize }}px</output>
        </div>
      </div>
      <div v-if="detailOpen" class="export-row">
        <select v-model="selectedFmt" aria-label="Định dạng xuất subtitle"><option v-for="format in exportFormats" :key="format" :value="format">.{{ format.toUpperCase() }}</option></select>
        <select v-model="selectedLayout" aria-label="Bố cục xuất subtitle"><option v-for="layout in exportLayouts" :key="layout.value" :value="layout.value">{{ layout.label }}</option></select>
        <button :disabled="exporting" @click="exportSubtitles"><Download :size="16" aria-hidden="true" />{{ exporting ? 'Đang xuất' : 'Xuất' }}</button>
      </div>
      <p v-if="detailOpen && exportMessage" class="export-message">{{ exportMessage }}</p>
    </aside>
  </section>
</template>

<style scoped>
.subtitle-overlay { position: absolute; inset: 0; z-index: 12; pointer-events: none; }
.subtitle-toolbar { position: absolute; top: var(--space-4); right: var(--space-4); display: flex; gap: var(--space-1); opacity: 0; pointer-events: none; transition: opacity var(--transition-fast); }
.subtitle-overlay.controls-visible .subtitle-toolbar, .subtitle-overlay.panel-open .subtitle-toolbar, .subtitle-overlay:focus-within .subtitle-toolbar { opacity: 1; pointer-events: auto; }
.toolbar-button { display: inline-flex; align-items: center; gap: var(--space-1); height: var(--control-height); padding: 0 var(--space-2); border: 0; border-radius: var(--radius-control); background: var(--bg-overlay); color: var(--text-primary); cursor: pointer; font-size: var(--font-meta); font-weight: 500; }
.toolbar-button:hover, .icon-button:hover { background: var(--bg-hover); }
.caption-card { position: absolute; left: 50%; bottom: var(--space-4); display: flex; flex-direction: column; align-items: center; gap: var(--space-1); width: max-content; max-width: min(90%, var(--caption-max-width)); padding: var(--space-2) var(--space-3); transform: translateX(-50%); border-radius: var(--radius-control); background: var(--bg-caption); color: var(--text-primary); font-weight: 500; line-height: 1.4; text-align: center; pointer-events: auto; cursor: pointer; text-wrap: balance; }
.subtitle-overlay.controls-visible .caption-card { bottom: var(--caption-offset); }
.caption-original { color: var(--text-secondary); font-size: .8em; font-weight: 400; }
.caption-translation { color: var(--text-primary); font-size: 1em; font-weight: 500; }
.caption-text { overflow-wrap: anywhere; user-select: text; -webkit-user-select: text; }
.cue-drawer { position: absolute; top: var(--drawer-top); right: var(--space-4); width: min(var(--popover-width), calc(100% - var(--drawer-inset))); max-height: calc(100% - var(--drawer-height-inset)); overflow: auto; padding: var(--space-4); border-radius: var(--radius-card); background: var(--bg-overlay-solid); color: var(--text-primary); box-shadow: var(--shadow-panel); pointer-events: auto; }
.drawer-header { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-3); }
.drawer-header strong { font-size: var(--font-file); font-weight: 600; }
.icon-button { display: grid; place-items: center; width: var(--control-height); height: var(--control-height); padding: 0; border: 0; border-radius: var(--radius-control); background: transparent; color: var(--text-secondary); cursor: pointer; }
.primary-switch { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-1); margin-bottom: var(--space-3); }
.primary-switch button, .export-row button { height: var(--control-height); border: 0; border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-secondary); cursor: pointer; }
.primary-switch button:hover, .export-row button:hover { color: var(--text-primary); }
.primary-switch button.selected { background: var(--bg-selected); color: var(--text-primary); }
.detail-line { padding: var(--space-2) 0; }
.detail-line > span { display: block; margin-bottom: var(--space-1); color: var(--text-muted); font-size: var(--font-meta); font-weight: 500; }
.detail-line p { margin: 0; line-height: 1.5; overflow-wrap: anywhere; }
.selectable-detail-text { cursor: text; user-select: text !important; -webkit-user-select: text !important; pointer-events: auto; }
.detail-line--original p { color: var(--text-secondary); }
.detail-line--translated p { color: var(--text-primary); font-weight: 500; }
.detail-line--originalPinyin p, .detail-line--translatedPinyin p { color: var(--text-muted); }
.display-settings { margin-top: var(--space-3); padding-top: var(--space-3); border-top: 1px solid var(--border-subtle); }
.display-settings > strong { color: var(--text-primary); font-size: var(--font-meta); font-weight: 600; }
.setting-row { display: grid; grid-template-columns: var(--control-height) var(--subtitle-label-width) 1fr var(--subtitle-output-width); align-items: center; gap: var(--space-1); margin-top: var(--space-2); color: var(--text-secondary); font-size: var(--font-meta); }
.setting-row input { width: 100%; }
.setting-row output { font-variant-numeric: tabular-nums; }
.export-row { display: grid; grid-template-columns: var(--export-format-width) 1fr var(--export-action-width); gap: var(--space-1); margin-top: var(--space-3); }
.export-row select { min-width: 0; border: 0; border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-primary); font-size: var(--font-meta); }
.export-row button { display: inline-flex; align-items: center; justify-content: center; gap: var(--space-1); }
.export-message { margin: var(--space-2) 0 0; color: var(--text-secondary); font-size: var(--font-meta); }
@media (max-width: 900px) { .subtitle-toolbar { top: var(--space-2); right: var(--space-2); } .cue-drawer { top: var(--drawer-compact-top); right: var(--space-2); max-height: calc(100% - var(--drawer-compact-height-inset)); } }
</style>
