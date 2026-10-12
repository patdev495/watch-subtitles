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
const primaryLine = 'translated' as const;
const secondaryLine = 'original' as const;
const detailOpen = ref(false);
const settingsOpen = ref(false);
const subtitlesVisible = ref(props.preferences?.overlay_visible ?? true);
const captionColor = ref(props.preferences?.caption_color ?? '#ffffff');
const captionBgOpacity = ref(props.preferences?.caption_bg_opacity ?? 0.86);
const chineseLanguage = (language: string): boolean => language.toLowerCase().startsWith('zh');
const originalPinyin = computed(() => activeCue.value && chineseLanguage(props.sourceLanguage)
  ? pinyin(activeCue.value.originalText, { toneType: 'symbol' }) : '');
const translatedPinyin = computed(() => activeCue.value && chineseLanguage(props.targetLanguage)
  ? pinyin(activeCue.value.translatedText, { toneType: 'symbol' }) : '');
const primaryText = computed(() => activeCue.value?.translatedText ?? '');
const secondaryText = computed(() => activeCue.value?.originalText ?? '');

const lineSettings = reactive<Record<SubtitleLine, { visible: boolean; fontSize: number }>>({
  original: { visible: props.preferences?.lines.original.visible ?? true, fontSize: props.preferences?.lines.original.font_size ?? 20 },
  originalPinyin: { visible: props.preferences?.lines.originalPinyin.visible ?? true, fontSize: props.preferences?.lines.originalPinyin.font_size ?? 15 },
  translated: { visible: props.preferences?.lines.translated.visible ?? true, fontSize: props.preferences?.lines.translated.font_size ?? 18 },
  translatedPinyin: { visible: props.preferences?.lines.translatedPinyin.visible ?? true, fontSize: props.preferences?.lines.translatedPinyin.font_size ?? 15 },
});
type DisplayMode = 'original' | 'translated' | 'bilingual';
const displayModes: { value: DisplayMode; label: string }[] = [
  { value: 'original', label: 'Chỉ gốc' },
  { value: 'translated', label: 'Chỉ bản dịch' },
  { value: 'bilingual', label: 'Cả hai' },
];
const displayMode = computed<DisplayMode>(() => {
  if (lineSettings.original.visible && !lineSettings.translated.visible) return 'original';
  if (!lineSettings.original.visible && lineSettings.translated.visible) return 'translated';
  return 'bilingual';
});
const hasCaption = computed(() => lineSettings.original.visible || lineSettings.translated.visible);
const captionCardStyle = computed(() => ({
  '--bg-opacity': String(captionBgOpacity.value),
}));
function snapshotPreferences(): SubtitleDisplayPreferences {
  return {
    primary_line: primaryLine, overlay_visible: subtitlesVisible.value, caption_color: captionColor.value,
    caption_bg_opacity: captionBgOpacity.value,
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
  subtitlesVisible.value = preferences.overlay_visible;
  captionColor.value = preferences.caption_color ?? '#ffffff';
  captionBgOpacity.value = preferences.caption_bg_opacity ?? 0.86;
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
function updateCaptionColor(event: Event): void { captionColor.value = (event.target as HTMLInputElement).value; notifyPreferences(); }
function updateCaptionBgOpacity(event: Event): void { captionBgOpacity.value = Number((event.target as HTMLInputElement).value); notifyPreferences(); }
function chooseDisplayMode(mode: DisplayMode): void {
  lineSettings.original.visible = mode !== 'translated';
  lineSettings.translated.visible = mode !== 'original';
  notifyPreferences();
}
function toggleSubtitles(): void { subtitlesVisible.value = !subtitlesVisible.value; notifyPreferences(); }
function toggleLine(line: SubtitleLine): void {
  lineSettings[line].visible = !lineSettings[line].visible;
  if ((line === 'original' || line === 'translated')
    && !lineSettings.original.visible && !lineSettings.translated.visible) {
    lineSettings[line === 'original' ? 'translated' : 'original'].visible = true;
  }
  notifyPreferences();
}
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

    <div v-if="subtitlesVisible && hasCaption" class="caption-card" :style="{ color: captionColor, ...captionCardStyle }" title="Nhấp để xem chi tiết phụ đề" role="button" tabindex="0" aria-label="Mở chi tiết phụ đề" @click="detailOpen = true" @keydown.enter="detailOpen = true" @keydown.space.prevent="detailOpen = true">
      <span v-if="lineSettings[secondaryLine].visible" :style="lineStyle(secondaryLine)" class="caption-line caption-original" :class="lineSettings[primaryLine].visible ? 'caption-secondary' : 'caption-text'"><span class="caption-pill">{{ secondaryText }}</span></span>
      <span v-if="lineSettings[primaryLine].visible" :style="lineStyle(primaryLine)" class="caption-line caption-text caption-translation"><span class="caption-pill">{{ primaryText }}</span></span>
    </div>

    <aside v-if="detailOpen || settingsOpen" class="cue-drawer" :aria-label="detailOpen ? 'Chi tiết phụ đề hiện tại' : 'Chỉnh hiển thị phụ đề'">
      <div class="drawer-header">
        <strong>{{ detailOpen ? 'Chi tiết câu hiện tại' : 'Chỉnh hiển thị' }}</strong>
        <button class="icon-button" aria-label="Đóng bảng phụ đề" @click="closePanel"><X :size="16" aria-hidden="true" /></button>
      </div>
      <div class="display-mode" role="group" aria-label="Chế độ hiển thị phụ đề">
        <button v-for="mode in displayModes" :key="mode.value" :class="{ selected: displayMode === mode.value }" :aria-pressed="displayMode === mode.value" @click="chooseDisplayMode(mode.value)">{{ mode.label }}</button>
      </div>
      <div v-for="line in detailOpen ? detailLines : []" :key="line.key" v-show="lineSettings[line.key].visible" class="detail-line" :class="`detail-line--${line.key}`">
        <span>{{ line.label }}</span>
        <p class="selectable-detail-text" @pointerdown.stop @mousedown.stop>{{ line.text }}</p>
      </div>
      <div v-if="settingsOpen" class="display-settings">
        <strong>Hiển thị, cỡ chữ &amp; màu chữ</strong>
        <div v-for="line in detailLines" :key="line.key" class="setting-row">
          <button class="icon-button" :aria-label="`${lineSettings[line.key].visible ? 'Ẩn' : 'Hiện'} dòng ${line.label}`" @click="toggleLine(line.key)">
            <Eye v-if="lineSettings[line.key].visible" :size="16" aria-hidden="true" /><EyeOff v-else :size="16" aria-hidden="true" />
          </button>
          <label :for="`font-${line.key}`">{{ line.label }}</label>
          <input :id="`font-${line.key}`" :aria-label="`Cỡ chữ dòng ${line.label}`" type="range" :min="line.minimum" max="36" :value="lineSettings[line.key].fontSize" @input="updateFontSize(line.key, $event)">
          <output>{{ lineSettings[line.key].fontSize }}px</output>
        </div>
        <div class="color-setting">
          <label for="caption-color">Màu chữ trên video</label>
          <input id="caption-color" type="color" :value="captionColor" aria-label="Màu chữ phụ đề" @input="updateCaptionColor">
          <output for="caption-color">{{ captionColor.toUpperCase() }}</output>
        </div>
        <div class="opacity-setting">
          <label for="caption-bg-opacity">Nền chữ trên video</label>
          <input id="caption-bg-opacity" type="range" min="0" max="1" step="0.01" :value="captionBgOpacity" aria-label="Độ trong suốt nền phụ đề" @input="updateCaptionBgOpacity">
          <output for="caption-bg-opacity">{{ Math.round(captionBgOpacity * 100) }}%</output>
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

<style scoped src="./TranscriptFooter.css"></style>

