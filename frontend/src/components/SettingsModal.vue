<script setup lang="ts">
import { ref, watch } from 'vue';
import { X, Key, Languages, TestTube2, CheckCircle2, XCircle } from 'lucide-vue-next';
import type { AppSettings, TestConnectionResponse } from '../types';
import { SUPPORTED_LANGUAGES } from '../languages';

const props = defineProps<{
  modelValue: boolean;
  initialSettings: AppSettings;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'saved', settings: AppSettings): void;
}>();

const form = ref<AppSettings>({ ...props.initialSettings });
watch(() => props.initialSettings, (v) => {
  form.value = { ...v };
  saveError.value = '';
});

const isSaving = ref(false);
const saveError = ref('');
const sttStatus = ref<TestConnectionResponse | null>(null);
const deeplStatus = ref<TestConnectionResponse | null>(null);
const isTestingStt = ref(false);
const isTestingDeepl = ref(false);

watch(() => form.value.deepgram_api_key, () => {
  sttStatus.value = null;
  saveError.value = '';
});

watch(() => form.value.assemblyai_api_key, () => {
  sttStatus.value = null;
  saveError.value = '';
});

watch(() => form.value.deepl_api_key, () => {
  deeplStatus.value = null;
  saveError.value = '';
});

watch(() => form.value.translation_provider, () => {
  deeplStatus.value = null;
  saveError.value = '';
});

watch(() => form.value.stt_provider, () => {
  sttStatus.value = null;
  saveError.value = '';
});

const LANGUAGE_OPTIONS = SUPPORTED_LANGUAGES.map(({ code: value, name: label }) => ({ value, label }));

async function testStt(): Promise<boolean> {
  const key = (form.value.stt_provider === 'assemblyai'
    ? form.value.assemblyai_api_key
    : form.value.deepgram_api_key).trim();
  if (!key) {
    sttStatus.value = null;
    return true;
  }
  isTestingStt.value = true;
  sttStatus.value = null;
  try {
    if (window.pywebview?.api) {
      const res = await window.pywebview.api.test_connection(
        'stt', form.value.stt_provider, key,
      );
      sttStatus.value = res;
      return res.ok;
    } else {
      sttStatus.value = { ok: false, message: 'pywebview bridge not available in browser mode' };
      return false;
    }
  } catch {
    sttStatus.value = { ok: false, message: 'Kiểm tra kết nối thất bại' };
    return false;
  } finally {
    isTestingStt.value = false;
  }
}

async function testDeepl(): Promise<boolean> {
  const key = form.value.translation_provider === 'deepl' ? form.value.deepl_api_key.trim() : '';
  if (form.value.translation_provider === 'deepl' && !key) {
    deeplStatus.value = null;
    return true;
  }
  isTestingDeepl.value = true;
  deeplStatus.value = null;
  try {
    if (window.pywebview?.api) {
      const res = await window.pywebview.api.test_connection(
        'translation', form.value.translation_provider, key,
      );
      deeplStatus.value = res;
      return res.ok;
    } else {
      deeplStatus.value = { ok: false, message: 'pywebview bridge not available in browser mode' };
      return false;
    }
  } catch {
    deeplStatus.value = { ok: false, message: 'Kiểm tra kết nối thất bại' };
    return false;
  } finally {
    isTestingDeepl.value = false;
  }
}

async function handleSave() {
  saveError.value = '';
  isSaving.value = true;

  try {
    // Kiểm tra tính hợp lệ của API key ngay lập tức trước khi lưu
    const [sttOk, deeplOk] = await Promise.all([
      testStt(),
      testDeepl(),
    ]);

    if (!sttOk || !deeplOk) {
      saveError.value = 'API key không hợp lệ. Vui lòng kiểm tra lại trước khi lưu.';
      return;
    }

    // Nếu hợp lệ -> lưu vào backend
    if (window.pywebview?.api) {
      const saved = await window.pywebview.api.save_settings({
        ...form.value,
        deepgram_api_key: form.value.deepgram_api_key.trim(),
        assemblyai_api_key: form.value.assemblyai_api_key.trim(),
        deepl_api_key: form.value.deepl_api_key.trim(),
      });
      emit('saved', saved);
    } else {
      // Dev-browser fallback
      emit('saved', {
        ...form.value,
        deepgram_api_key: form.value.deepgram_api_key.trim(),
        assemblyai_api_key: form.value.assemblyai_api_key.trim(),
        deepl_api_key: form.value.deepl_api_key.trim(),
      });
    }
    emit('update:modelValue', false);
  } catch (err) {
    console.error('Failed to save settings:', err);
    saveError.value = 'Không thể lưu cài đặt. Vui lòng thử lại.';
  } finally {
    isSaving.value = false;
  }
}

function close() {
  emit('update:modelValue', false);
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modelValue" class="modal-backdrop" @click.self="close">
        <div class="modal-card" role="dialog" aria-modal="true" aria-label="Cài đặt">
          <!-- Header -->
          <div class="modal-header">
            <div class="modal-title-row">
              <Key :size="16" class="modal-title-icon" />
              <h2 class="modal-title">Cài đặt API</h2>
            </div>
            <button class="icon-close" @click="close" aria-label="Đóng">
              <X :size="16" />
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- Save error message banner -->
            <div v-if="saveError" class="save-error-banner">
              <XCircle :size="16" />
              <span>{{ saveError }}</span>
            </div>

            <!-- Transcription provider -->
            <section class="settings-section">
              <div class="section-label">
                <span class="section-title">Nhận diện giọng nói (STT)</span>
                <span class="section-badge">{{ form.stt_provider }}</span>
              </div>
              <label class="sr-only" for="stt-provider">Dịch vụ nhận diện giọng nói</label>
              <select id="stt-provider" v-model="form.stt_provider" class="field-select">
                <option value="deepgram">Deepgram — cần API key</option>
                <option value="assemblyai">AssemblyAI — cần API key</option>
              </select>
              <div v-if="form.stt_provider === 'deepgram'" class="field-row">
                <input
                  id="deepgram-key"
                  v-model="form.deepgram_api_key"
                  type="password"
                  class="field-input"
                  placeholder="dgk-xxxxxxxxxxxxxxxx"
                  autocomplete="off"
                />
                <button
                  class="btn-test"
                  :disabled="!form.deepgram_api_key || isTestingStt"
                  @click="testStt"
                >
                  <TestTube2 :size="16" />
                  {{ isTestingStt ? 'Kiểm tra...' : 'Test' }}
                </button>
              </div>
              <div v-else class="field-row">
                <input
                  id="assemblyai-key"
                  v-model="form.assemblyai_api_key"
                  type="password"
                  class="field-input"
                  placeholder="AssemblyAI API key"
                  autocomplete="off"
                />
                <button
                  class="btn-test"
                  :disabled="!form.assemblyai_api_key || isTestingStt"
                  @click="testStt"
                >
                  <TestTube2 :size="16" />
                  {{ isTestingStt ? 'Kiểm tra...' : 'Test' }}
                </button>
              </div>
              <div v-if="sttStatus" class="status-row">
                <component
                  :is="sttStatus.ok ? CheckCircle2 : XCircle"
                  :size="16"
                  :class="sttStatus.ok ? 'status-ok' : 'status-err'"
                />
                <span :class="sttStatus.ok ? 'status-ok' : 'status-err'">
                  {{ sttStatus.message }}
                </span>
              </div>
            </section>

            <!-- Translation provider -->
            <section class="settings-section">
              <div class="section-label">
                <span class="section-title">Dịch phụ đề</span>
                <span class="section-badge">{{ form.translation_provider }}</span>
              </div>
              <label class="sr-only" for="translation-provider">Dịch vụ dịch</label>
              <select id="translation-provider" v-model="form.translation_provider" class="field-select">
                <option value="deepl">DeepL — cần API key</option>
                <option value="google">Google Translate — miễn phí, không cần key</option>
              </select>
              <div v-if="form.translation_provider === 'deepl'" class="field-row">
                <input
                  id="deepl-key"
                  v-model="form.deepl_api_key"
                  type="password"
                  class="field-input"
                  placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx"
                  autocomplete="off"
                />
                <button
                  class="btn-test"
                  :disabled="!form.deepl_api_key || isTestingDeepl"
                  @click="testDeepl"
                >
                  <TestTube2 :size="16" />
                  {{ isTestingDeepl ? 'Kiểm tra...' : 'Test' }}
                </button>
              </div>
              <div v-else class="provider-note">
                <span>Google Translate không cần API key.</span>
                <button class="btn-test" :disabled="isTestingDeepl" @click="testDeepl"><TestTube2 :size="16" />{{ isTestingDeepl ? 'Kiểm tra...' : 'Test kết nối' }}</button>
              </div>
              <div v-if="deeplStatus" class="status-row">
                <component
                  :is="deeplStatus.ok ? CheckCircle2 : XCircle"
                  :size="16"
                  :class="deeplStatus.ok ? 'status-ok' : 'status-err'"
                />
                <span :class="deeplStatus.ok ? 'status-ok' : 'status-err'">
                  {{ deeplStatus.message }}
                </span>
              </div>
            </section>

            <!-- Target Language -->
            <section class="settings-section">
              <div class="section-label">
                <Languages :size="16" class="section-icon" />
                <span class="section-title">Ngôn ngữ dịch mặc định</span>
              </div>
              <select
                id="target-language"
                v-model="form.default_target_language"
                class="field-select"
              >
                <option
                  v-for="opt in LANGUAGE_OPTIONS"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>
            </section>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn-cancel" @click="close">Huỷ</button>
            <button class="btn-save" :disabled="isSaving" @click="handleSave">
              {{ isSaving ? 'Đang kiểm tra & lưu...' : 'Lưu cài đặt' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; z-index: 9000; display: flex; align-items: center; justify-content: center; padding: var(--space-4); background: var(--bg-backdrop); }
.modal-card { display: flex; flex-direction: column; width: var(--settings-width); max-width: 100%; max-height: 92vh; overflow: auto; border-radius: var(--radius-card); background: var(--bg-surface); box-shadow: var(--shadow-panel); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: var(--space-4) var(--space-6); border-bottom: 1px solid var(--border-subtle); }
.modal-title-row { display: flex; align-items: center; gap: var(--space-2); }
.modal-title-icon, .section-icon { color: var(--text-secondary); }
.modal-title { margin: 0; color: var(--text-primary); font-size: var(--font-title); font-weight: 600; }
.icon-close { display: grid; place-items: center; width: var(--control-height); height: var(--control-height); border: 0; border-radius: var(--radius-control); background: transparent; color: var(--text-secondary); cursor: pointer; }
.icon-close:hover { background: var(--bg-hover); color: var(--text-primary); }
.modal-body { display: flex; flex-direction: column; gap: var(--space-5); padding: var(--space-5) var(--space-6); }
.save-error-banner { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-3); border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-primary); font-size: var(--font-meta); }
.settings-section { display: flex; flex-direction: column; gap: var(--space-2); }
.section-label { display: flex; align-items: center; gap: var(--space-2); }
.section-title { color: var(--text-secondary); font-size: var(--font-meta); font-weight: 600; }
.section-badge { padding: 0 var(--space-1); border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-secondary); font-size: var(--font-meta); }
.field-row, .provider-note { display: flex; gap: var(--space-2); }
.provider-note { align-items: center; justify-content: space-between; color: var(--text-secondary); font-size: var(--font-meta); }
.field-input, .field-select { min-width: 0; min-height: var(--control-height); padding: 0 var(--space-3); border: 1px solid var(--border-subtle); border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-primary); font-size: var(--font-body); }
.field-input { flex: 1; }
.field-input::placeholder { color: var(--text-muted); }
.field-select { width: 100%; }
.btn-test { display: inline-flex; align-items: center; gap: var(--space-1); padding: 0 var(--space-3); border: 0; border-radius: var(--radius-control); background: var(--bg-hover); color: var(--text-secondary); font-size: var(--font-meta); cursor: pointer; white-space: nowrap; }
.btn-test:hover:not(:disabled) { background: var(--bg-selected); color: var(--text-primary); }
.status-row { display: flex; align-items: center; gap: var(--space-1); font-size: var(--font-meta); }
.status-ok, .status-err { color: var(--text-secondary); }
.modal-footer { display: flex; align-items: center; justify-content: flex-end; gap: var(--space-2); padding: var(--space-4) var(--space-6); border-top: 1px solid var(--border-subtle); }
.btn-cancel, .btn-save { min-height: var(--control-height); padding: 0 var(--space-3); border: 0; border-radius: var(--radius-control); font-size: var(--font-body); font-weight: 500; cursor: pointer; }
.btn-cancel { background: transparent; color: var(--text-secondary); }
.btn-cancel:hover { background: var(--bg-hover); color: var(--text-primary); }
.btn-save { background: var(--accent-primary); color: var(--accent-contrast); }
.btn-save:hover:not(:disabled) { opacity: .88; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity var(--transition-fast); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
