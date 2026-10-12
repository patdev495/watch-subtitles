import { ref } from 'vue';
import type { ThemeName } from '../types';

const STORAGE_KEY = 'watch-subtitles:theme';
const theme = ref<ThemeName>('dark');

function isThemeName(value: unknown): value is ThemeName {
  return value === 'dark' || value === 'light';
}

function readStoredTheme(): ThemeName | null {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return isThemeName(stored) ? stored : null;
  } catch {
    return null;
  }
}

function storeTheme(value: ThemeName): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, value);
  } catch {
    /* storage can be unavailable; the theme still applies for this session */
  }
}

function applyTheme(value: ThemeName): void {
  theme.value = value;
  document.documentElement.dataset.theme = value;
}

/** Apply the persisted theme before the app mounts, so no wrong-theme frame is painted. */
export function initThemeFromStorage(): void {
  applyTheme(readStoredTheme() ?? 'dark');
}

export function useTheme() {
  /** Reconcile with the backend value once the pywebview bridge is available. */
  async function loadTheme(): Promise<void> {
    const stored = readStoredTheme();
    if (stored) applyTheme(stored);
    if (!window.pywebview?.api?.get_theme) return;
    try {
      const res = await window.pywebview.api.get_theme();
      if (isThemeName(res?.theme)) applyTheme(res.theme);
    } catch (error) {
      console.error('Failed to restore theme:', error);
    }
  }

  function setTheme(value: ThemeName): void {
    applyTheme(value);
    storeTheme(value);
    const api = window.pywebview?.api;
    if (!api?.save_theme) return;
    void api.save_theme(value).catch((error: unknown) => {
      console.error('Failed to save theme:', error);
    });
  }

  function toggleTheme(): void {
    setTheme(theme.value === 'dark' ? 'light' : 'dark');
  }

  return { theme, loadTheme, setTheme, toggleTheme };
}
