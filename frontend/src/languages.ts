export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'vi', name: 'Tiếng Việt' },
  { code: 'zh-CN', name: '中文（简体）' },
  { code: 'zh-TW', name: '中文（繁體）' },
] as const;

export const AUTO_DETECT_LANGUAGE = 'auto';

export const SUPPORTED_SOURCE_LANGUAGES = [
  { code: AUTO_DETECT_LANGUAGE, name: 'Tự động phát hiện' },
  ...SUPPORTED_LANGUAGES,
] as const;
