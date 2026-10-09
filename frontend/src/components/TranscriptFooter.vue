<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { Download, Eye, EyeOff, Info, SlidersHorizontal, X } from 'lucide-vue-next';
import { pinyin } from 'pinyin-pro';
import type { Cue } from '../types';
import { useTranscript } from '../composables/useTranscript';

const props = defineProps<{
  cues: Cue[];
  currentTime: number;
  sourceLanguage: string;
  targetLanguage: string;
}>();

type SubtitleLine = 'original' | 'originalPinyin' | 'translated' | 'translatedPinyin';

const cuesRef = computed(() => props.cues);
const currentTimeRef = computed(() => props.currentTime);
const { activeCue } = useTranscript(cuesRef, currentTimeRef);
const primaryLine = ref<'original' | 'translated'>('translated');
const detailOpen = ref(false);
const settingsOpen = ref(false);
const subtitlesVisible = ref(true);
const chineseLanguage = (language: string): boolean => language.toLowerCase().startsWith('zh');
const originalPinyin = computed(() => activeCue.value && chineseLanguage(props.sourceLanguage)
  ? pinyin(activeCue.value.originalText, { toneType: 'symbol' }) : '');
const translatedPinyin = computed(() => activeCue.value && chineseLanguage(props.targetLanguage)
  ? pinyin(activeCue.value.translatedText, { toneType: 'symbol' }) : '');
const primaryText = computed(() => activeCue.value
  ? primaryLine.value === 'original' ? activeCue.value.originalText : activeCue.value.translatedText
  : '');

const lineSettings = reactive<Record<SubtitleLine, { visible: boolean; fontSize: number }>>({
  original: { visible: true, fontSize: 20 }, originalPinyin: { visible: true, fontSize: 15 },
  translated: { visible: true, fontSize: 18 }, translatedPinyin: { visible: true, fontSize: 15 },
});
const detailLines = computed(() => [
  { key: 'original' as const, label: 'Gốc', text: activeCue.value?.originalText ?? '', minimum: 12 },
  ...(originalPinyin.value ? [{ key: 'originalPinyin' as const, label: 'Pinyin gốc', text: originalPinyin.value, minimum: 10 }] : []),
  { key: 'translated' as const, label: 'Dịch', text: activeCue.value?.translatedText ?? '', minimum: 12 },
  ...(translatedPinyin.value ? [{ key: 'translatedPinyin' as const, label: 'Pinyin dịch', text: translatedPinyin.value, minimum: 10 }] : []),
]);

function lineStyle(line: SubtitleLine): { fontSize: string } { return { fontSize: `${lineSettings[line].fontSize}px` }; }
function updateFontSize(line: SubtitleLine, event: Event): void { lineSettings[line].fontSize = Number((event.target as HTMLInputElement).value); }
function choosePrimary(line: 'original' | 'translated'): void { primaryLine.value = line; }
function toggleSubtitles(): void { subtitlesVisible.value = !subtitlesVisible.value; }
function closePanel(): void { detailOpen.value = false; settingsOpen.value = false; }

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
  <section v-if="activeCue" class="subtitle-overlay" aria-label="Phụ đề hiện tại">
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
        @click="settingsOpen = !settingsOpen"
      >
        <SlidersHorizontal :size="18" aria-hidden="true" />
        <span>Aa</span>
      </button>
    </div>

    <button v-if="subtitlesVisible && lineSettings[primaryLine].visible" class="caption-card" :style="lineStyle(primaryLine)" aria-label="Mở chi tiết phụ đề" @click="detailOpen = true">
      <span>{{ primaryText }}</span>
      <Info :size="15" aria-hidden="true" />
    </button>

    <aside v-if="detailOpen || settingsOpen" class="cue-drawer" :aria-label="detailOpen ? 'Chi tiết phụ đề hiện tại' : 'Chỉnh hiển thị phụ đề'">
      <div class="drawer-header">
        <strong>{{ detailOpen ? 'Chi tiết câu hiện tại' : 'Chỉnh hiển thị' }}</strong>
        <button class="icon-button" aria-label="Đóng bảng phụ đề" @click="closePanel"><X :size="17" aria-hidden="true" /></button>
      </div>
      <div v-if="detailOpen || settingsOpen" class="primary-switch" aria-label="Dòng sub trên video">
        <button :class="{ selected: primaryLine === 'original' }" :aria-pressed="primaryLine === 'original'" aria-label="Hiển thị dòng gốc trên video" @click="choosePrimary('original')">Gốc</button>
        <button :class="{ selected: primaryLine === 'translated' }" :aria-pressed="primaryLine === 'translated'" aria-label="Hiển thị dòng dịch trên video" @click="choosePrimary('translated')">Dịch</button>
      </div>
      <div v-for="line in detailOpen ? detailLines : []" :key="line.key" v-show="lineSettings[line.key].visible" class="detail-line" :class="`detail-line--${line.key}`">
        <span>{{ line.label }}</span>
        <p :style="lineStyle(line.key)">{{ line.text }}</p>
      </div>
      <div v-if="settingsOpen" class="display-settings">
        <strong>Hiển thị &amp; cỡ chữ</strong>
        <div v-for="line in detailLines" :key="line.key" class="setting-row">
          <button class="icon-button" :aria-label="`${lineSettings[line.key].visible ? 'Ẩn' : 'Hiện'} dòng ${line.label}`" @click="lineSettings[line.key].visible = !lineSettings[line.key].visible">
            <Eye v-if="lineSettings[line.key].visible" :size="15" aria-hidden="true" /><EyeOff v-else :size="15" aria-hidden="true" />
          </button>
          <label :for="`font-${line.key}`">{{ line.label }}</label>
          <input :id="`font-${line.key}`" :aria-label="`Cỡ chữ dòng ${line.label}`" type="range" :min="line.minimum" max="36" :value="lineSettings[line.key].fontSize" @input="updateFontSize(line.key, $event)">
          <output>{{ lineSettings[line.key].fontSize }}px</output>
        </div>
      </div>
      <div v-if="detailOpen" class="export-row">
        <select v-model="selectedFmt" aria-label="Định dạng xuất subtitle"><option v-for="format in exportFormats" :key="format" :value="format">.{{ format.toUpperCase() }}</option></select>
        <select v-model="selectedLayout" aria-label="Bố cục xuất subtitle"><option v-for="layout in exportLayouts" :key="layout.value" :value="layout.value">{{ layout.label }}</option></select>
        <button :disabled="exporting" @click="exportSubtitles"><Download :size="15" aria-hidden="true" />{{ exporting ? 'Đang xuất' : 'Xuất' }}</button>
      </div>
      <p v-if="detailOpen && exportMessage" class="export-message">{{ exportMessage }}</p>
    </aside>
  </section>
</template>

<style scoped>
.subtitle-overlay { position: absolute; inset: 0; z-index: 12; pointer-events: none; }
.subtitle-toolbar { position: absolute; top: 14px; right: 14px; display: flex; gap: 6px; pointer-events: auto; }
.toolbar-button { display: inline-flex; align-items: center; gap: 5px; min-height: 36px; padding: 0 10px; border: 1px solid rgba(148, 163, 184, .42); border-radius: 8px; color: #f8fafc; background: rgba(2, 6, 23, .82); box-shadow: 0 4px 18px rgba(0, 0, 0, .35); cursor: pointer; font-size: 12px; font-weight: 700; }
.toolbar-button:hover, .toolbar-button:focus-visible, .icon-button:focus-visible { border-color: #93c5fd; background: #172033; outline: 2px solid transparent; }
.caption-card { position: absolute; left: 50%; bottom: 18px; display: inline-flex; align-items: center; gap: 8px; max-width: min(78%, 760px); padding: 8px 14px; transform: translateX(-50%); border: 1px solid rgba(255, 255, 255, .22); border-radius: 8px; color: #f8fafc; background: rgba(2, 6, 23, .82); box-shadow: 0 4px 18px rgba(0, 0, 0, .42); line-height: 1.45; text-align: center; cursor: pointer; pointer-events: auto; }
.caption-card:hover { background: rgba(15, 23, 42, .94); }.caption-card span { overflow-wrap: anywhere; }.caption-card svg { flex: 0 0 auto; color: #93c5fd; }
.cue-drawer { position: absolute; top: 58px; right: 14px; width: min(360px, calc(100% - 28px)); max-height: calc(100% - 72px); overflow: auto; padding: 14px; border: 1px solid rgba(148, 163, 184, .4); border-radius: 12px; color: #e2e8f0; background: rgba(2, 6, 23, .96); box-shadow: 0 16px 42px rgba(0, 0, 0, .55); pointer-events: auto; }
.drawer-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }.drawer-header strong { font-size: 14px; }.icon-button { display: inline-flex; align-items: center; justify-content: center; min-width: 30px; min-height: 30px; padding: 0; border: 1px solid rgba(148, 163, 184, .42); border-radius: 6px; color: #e2e8f0; background: #172033; cursor: pointer; }
.primary-switch { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 14px; }.primary-switch button, .export-row button { min-height: 30px; border: 1px solid rgba(148, 163, 184, .42); border-radius: 6px; color: #e2e8f0; background: #172033; cursor: pointer; }.primary-switch button.selected { color: #fff; background: #2563eb; border-color: #60a5fa; }
.detail-line { padding: 9px 0; border-top: 1px solid rgba(148, 163, 184, .2); }.detail-line > span { display: block; margin-bottom: 4px; color: #94a3b8; font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }.detail-line p { margin: 0; line-height: 1.5; overflow-wrap: anywhere; }.detail-line--original p { color: #f8fafc; }.detail-line--translated p { color: #fde68a; }.detail-line--originalPinyin p, .detail-line--translatedPinyin p { color: #67e8f9; font-style: italic; }
.display-settings { margin-top: 10px; border-top: 1px solid rgba(148, 163, 184, .2); padding-top: 10px; }.display-settings > strong { color: #93c5fd; font-size: 12px; font-weight: 700; }.setting-row { display: grid; grid-template-columns: 30px 76px 1fr 36px; align-items: center; gap: 6px; margin-top: 8px; color: #cbd5e1; font-size: 12px; }.setting-row input { width: 100%; accent-color: #60a5fa; }.setting-row output { font-variant-numeric: tabular-nums; }
.export-row { display: grid; grid-template-columns: 68px 1fr 64px; gap: 6px; margin-top: 14px; }.export-row select { min-width: 0; border: 1px solid rgba(148, 163, 184, .42); border-radius: 6px; color: #e2e8f0; background: #172033; font-size: 12px; }.export-row button { display: inline-flex; align-items: center; justify-content: center; gap: 4px; background: #2563eb; }.export-message { margin: 8px 0 0; color: #86efac; font-size: 12px; }
@media (max-width: 720px) { .subtitle-toolbar { top: 8px; right: 8px; }.toolbar-button { min-height: 34px; padding: 0 8px; }.caption-card { bottom: 14px; max-width: calc(100% - 24px); }.cue-drawer { top: 50px; right: 8px; width: min(340px, calc(100% - 16px)); max-height: calc(100% - 58px); } }
</style>
