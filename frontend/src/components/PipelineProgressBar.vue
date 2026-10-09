<script setup lang="ts">
import { computed } from 'vue';
import { Loader2, CheckCircle2, AlertTriangle, X, Sparkles, Mic, Languages, FileCheck } from 'lucide-vue-next';
import type { PipelineStatus } from '../types';

const props = defineProps<{
  modelValue: boolean;
  status: PipelineStatus;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'close'): void;
}>();

const steps = [
  { id: 1, label: 'Trích xuất audio', range: [0, 20], icon: Mic },
  { id: 2, label: 'Nhận diện Deepgram', range: [20, 60], icon: Sparkles },
  { id: 3, label: 'Dịch thuật DeepL', range: [60, 90], icon: Languages },
  { id: 4, label: 'Lưu & Hoàn tất', range: [90, 100], icon: FileCheck },
];

const currentStepId = computed(() => {
  const p = props.status.progress;
  if (p < 20) return 1;
  if (p < 60) return 2;
  if (p < 90) return 3;
  return 4;
});

function handleClose(): void {
  emit('update:modelValue', false);
  emit('close');
}
</script>

<template>
  <div v-if="modelValue" class="pipeline-backdrop">
    <div class="pipeline-card" role="dialog" aria-modal="true">
      <!-- Header -->
      <div class="pipeline-header">
        <div class="header-left">
          <div class="header-icon-wrapper" :class="{ error: status.status === 'error', done: status.status === 'completed' }">
            <AlertTriangle v-if="status.status === 'error'" :size="20" class="text-rose-400" />
            <CheckCircle2 v-else-if="status.status === 'completed'" :size="20" class="text-emerald-400" />
            <Loader2 v-else :size="20" class="spin text-indigo-400" />
          </div>
          <div class="header-titles">
            <h3 class="pipeline-title">
              <span v-if="status.status === 'error'">Lỗi Tạo Phụ Đề</span>
              <span v-else-if="status.status === 'completed'">Tạo Phụ Đề Hoàn Tất!</span>
              <span v-else>Đang Xử Lý Phụ Đề Tự Động</span>
            </h3>
            <p class="pipeline-subtitle">{{ status.step || 'Đang kết nối backend...' }}</p>
          </div>
        </div>

        <button
          v-if="status.status === 'error' || status.status === 'completed'"
          class="btn-close"
          title="Đóng"
          @click="handleClose"
        >
          <X :size="18" />
        </button>
      </div>

      <!-- Step Indicator -->
      <div class="steps-container">
        <div
          v-for="st in steps"
          :key="st.id"
          class="step-pill"
          :class="{
            active: currentStepId === st.id && status.status === 'running',
            completed: currentStepId > st.id || status.status === 'completed',
          }"
        >
          <component :is="st.icon" :size="14" class="step-icon" />
          <span class="step-name">{{ st.label }}</span>
        </div>
      </div>

      <!-- Progress bar -->
      <div class="progress-section">
        <div class="progress-info">
          <span class="progress-stage-name">Tiến độ quy trình</span>
          <span class="progress-percent">{{ Math.round(status.progress) }}%</span>
        </div>
        <div class="progress-track">
          <div
            class="progress-fill"
            :class="{ error: status.status === 'error', complete: status.status === 'completed' }"
            :style="{ width: `${status.progress}%` }"
          ></div>
        </div>
      </div>

      <!-- Error box if present -->
      <div v-if="status.status === 'error' && status.error" class="error-banner">
        <AlertTriangle :size="16" class="error-banner-icon" />
        <span class="error-banner-text">{{ status.error }}</span>
      </div>

      <!-- Footer button -->
      <div v-if="status.status === 'completed' || status.status === 'error'" class="pipeline-footer">
        <button class="btn-done" @click="handleClose">
          {{ status.status === 'completed' ? 'Đóng và Trải Nghiệm' : 'Đóng' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pipeline-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 7, 18, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.pipeline-card {
  width: 100%;
  max-width: 540px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(99, 102, 241, 0.2);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: popIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.pipeline-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon-wrapper.error {
  background: rgba(244, 63, 94, 0.15);
  border-color: rgba(244, 63, 94, 0.3);
}

.header-icon-wrapper.done {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
}

.spin {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pipeline-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #f8fafc;
}

.pipeline-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: #94a3b8;
}

.btn-close {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: color 0.15s;
}
.btn-close:hover {
  color: #cbd5e1;
}

/* Steps */
.steps-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.step-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 6px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  text-align: center;
  color: #64748b;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.step-pill.active {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.4);
  color: #c7d2fe;
}

.step-pill.completed {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #6ee7b7;
}

/* Progress track */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
}

.progress-track {
  height: 8px;
  width: 100%;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 9999px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #38bdf8);
  border-radius: 9999px;
  transition: width 0.35s ease;
}

.progress-fill.complete {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.progress-fill.error {
  background: #f43f5e;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.3);
  border-radius: 10px;
  color: #fda4af;
  font-size: 13px;
}

.error-banner-icon {
  flex-shrink: 0;
  color: #f43f5e;
}

.pipeline-footer {
  display: flex;
  justify-content: flex-end;
}

.btn-done {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  background: linear-gradient(135deg, #6366f1, #38bdf8);
  color: #ffffff;
  border: none;
  cursor: pointer;
  transition: filter 0.15s;
}
.btn-done:hover {
  filter: brightness(1.1);
}
</style>
