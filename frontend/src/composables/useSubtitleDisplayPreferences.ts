import { ref } from 'vue';
import type { SubtitleDisplayPreferences } from '../types';

function defaultPreferences(): SubtitleDisplayPreferences {
  return {
    primary_line: 'translated', overlay_visible: true, caption_color: '#ffffff', caption_bg_opacity: 0.86,
    lines: {
      original: { visible: true, font_size: 20 }, originalPinyin: { visible: true, font_size: 15 },
      translated: { visible: true, font_size: 18 }, translatedPinyin: { visible: true, font_size: 15 },
    },
  };
}

/** Subtitle overlay preferences: restored from the backend and saved on every change. */
export function useSubtitleDisplayPreferences() {
  const displayPreferences = ref<SubtitleDisplayPreferences>(defaultPreferences());
  let savePending: Promise<void> = Promise.resolve();

  async function loadDisplayPreferences(): Promise<void> {
    const api = window.pywebview?.api;
    if (!api?.get_subtitle_display_preferences) return;
    try { displayPreferences.value = await api.get_subtitle_display_preferences(); }
    catch (error) { console.error('Failed to restore subtitle display preferences:', error); }
  }

  function saveDisplayPreferences(preferences: SubtitleDisplayPreferences): void {
    displayPreferences.value = preferences;
    const api = window.pywebview?.api;
    if (!api?.save_subtitle_display_preferences) return;
    savePending = savePending.then(async () => {
      await api.save_subtitle_display_preferences(preferences);
    }).catch((error: unknown) => { console.error('Failed to save subtitle display preferences:', error); });
  }

  return { displayPreferences, loadDisplayPreferences, saveDisplayPreferences };
}
