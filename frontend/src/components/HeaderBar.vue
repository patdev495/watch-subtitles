<script setup lang="ts">
import { Clapperboard, FileVideo, FolderOpen, Settings, Subtitles, Activity } from 'lucide-vue-next';

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
  <header class="h-14 px-4 flex items-center justify-between glass-panel border-b border-[var(--border-subtle)] z-50 select-none">
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-lg bg-[var(--bg-raised)] border border-[var(--border-subtle)] grid place-items-center text-[var(--accent)] shadow-inner">
          <Clapperboard :size="18" :stroke-width="2" />
        </div>
        <span class="font-bold tracking-tight text-white flex items-center gap-1.5">
          WatchSub Studio <span class="text-[10px] uppercase px-1.5 py-0.5 rounded bg-[var(--accent)] text-white font-semibold">Pro</span>
        </span>
      </div>

      <div class="h-5 w-[1px] bg-[var(--border-subtle)] mx-1"></div>

      <div class="flex items-center gap-2.5 max-w-md truncate text-sm text-[var(--text-secondary)]">
        <div class="w-7 h-7 rounded bg-[var(--bg-raised)] border border-[var(--border-subtle)] grid place-items-center flex-shrink-0 text-[var(--text-muted)]">
          <FileVideo :size="15" />
        </div>
        <div class="truncate flex flex-col leading-tight">
          <strong class="text-white font-medium truncate">{{ currentFilename || 'Chưa chọn video' }}</strong>
          <span class="text-[11px] flex items-center gap-1.5 text-[var(--text-muted)]">
            <span class="w-1.5 h-1.5 rounded-full" :class="hasSubtitles ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-zinc-600'"></span>
            {{ hasSubtitles ? 'Đã có phụ đề song ngữ' : 'Chưa có phụ đề' }}
          </span>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <button
        class="w-9 h-9 rounded-lg bg-[var(--bg-raised)] border border-[var(--border-subtle)] grid place-items-center text-[var(--text-secondary)] hover:text-white hover:bg-[var(--bg-hover)] transition-all"
        :class="{ 'border-emerald-500/50 text-emerald-400': backendConnected }"
        :title="backendConnected ? 'Backend đã kết nối' : 'Kiểm tra kết nối backend'"
        @click="emit('ping-backend')"
      >
        <Activity :size="16" />
      </button>

      <button
        class="w-9 h-9 rounded-lg bg-[var(--bg-raised)] border border-[var(--border-subtle)] grid place-items-center text-[var(--text-secondary)] hover:text-white hover:bg-[var(--bg-hover)] transition-all"
        title="Cài đặt API"
        @click="emit('open-settings')"
      >
        <Settings :size="16" />
      </button>

      <button
        class="subtitle-button h-9 px-3.5 rounded-lg bg-[var(--bg-raised)] border border-[var(--border-subtle)] text-sm font-medium text-white hover:bg-[var(--bg-hover)] flex items-center gap-2 transition-all shadow-sm"
        aria-label="Phụ đề"
        title="Phụ đề"
        @click="emit('open-subtitles')"
      >
        <Subtitles :size="16" class="text-[var(--accent)]" />
        <span>Tạo phụ đề</span>
      </button>

      <button
        class="open-button h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-sm font-semibold flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(99,102,241,0.3)]"
        @click="emit('open-video')"
      >
        <FolderOpen :size="16" />
        <span>Mở video</span>
      </button>
    </div>
  </header>
</template>
