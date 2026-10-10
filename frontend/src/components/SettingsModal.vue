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
              <XCircle :size="15" />
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
                  <TestTube2 :size="13" />
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
                  <TestTube2 :size="13" />
                  {{ isTestingStt ? 'Kiểm tra...' : 'Test' }}
                </button>
              </div>
              <div v-if="sttStatus" class="status-row">
                <component
                  :is="sttStatus.ok ? CheckCircle2 : XCircle"
                  :size="13"
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
                  <TestTube2 :size="13" />
                  {{ isTestingDeepl ? 'Kiểm tra...' : 'Test' }}
                </button>
              </div>
              <div v-else class="provider-note">
                <span>Google Translate không cần API key.</span>
                <button class="btn-test" :disabled="isTestingDeepl" @click="testDeepl"><TestTube2 :size="13" />{{ isTestingDeepl ? 'Kiểm tra...' : 'Test kết nối' }}</button>
              </div>
              <div v-if="deeplStatus" class="status-row">
                <component
                  :is="deeplStatus.ok ? CheckCircle2 : XCircle"
                  :size="13"
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
                <Languages :size="14" class="section-icon" />
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
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(3, 7, 18, 0.75);
  backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; z-index: 9000;
}
.modal-card {
  width: 480px; max-width: calc(100vw - 32px); background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(99, 102, 241, 0.15);
  display: flex; flex-direction: column; overflow: hidden;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.modal-title-row { display: flex; align-items: center; gap: 10px; }
.modal-title-icon { color: #6366f1; }
.modal-title { font-size: 15px; font-weight: 700; color: #f1f5f9; margin: 0; }
.icon-close {
  width: 28px; height: 28px; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.08);
  background: transparent; color: #64748b; cursor: pointer; display: flex;
  align-items: center; justify-content: center; transition: background 0.1s, color 0.1s;
}
.icon-close:hover { background: rgba(255, 255, 255, 0.06); color: #e2e8f0; }
.modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 20px; }
.save-error-banner {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px; color: #fca5a5; font-size: 12px; font-weight: 500;
}
.settings-section { display: flex; flex-direction: column; gap: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; }
.section-icon { color: #6366f1; }
.section-title {
  font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em;
}
.section-badge {
  font-size: 10px; padding: 2px 7px; border-radius: 10px;
  background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.25);
  color: #818cf8; font-weight: 600;
}
.field-row { display: flex; gap: 8px; }
.provider-note { display: flex; align-items: center; justify-content: space-between; gap: 10px; color: #94a3b8; font-size: 12px; }
.field-input {
  flex: 1; padding: 9px 12px; background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px;
  color: #e2e8f0; font-size: 13px; font-family: 'JetBrains Mono', monospace;
  outline: none; transition: border-color 0.15s;
}
.field-input::placeholder { color: #334155; }
.field-input:focus { border-color: rgba(99, 102, 241, 0.5); }
.field-select {
  width: 100%; padding: 9px 12px; background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px;
  color: #e2e8f0; font-size: 13px; outline: none; cursor: pointer; transition: border-color 0.15s;
}
.field-select:focus { border-color: rgba(99, 102, 241, 0.5); }
.field-select option { background: #1e293b; }
.btn-test {
  display: flex; align-items: center; gap: 5px; padding: 0 14px; border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.04);
  color: #94a3b8; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}
.btn-test:hover:not(:disabled) { background: rgba(99, 102, 241, 0.12); color: #818cf8; }
.btn-test:disabled { opacity: 0.4; cursor: not-allowed; }
.status-row { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.status-ok { color: #34d399; }
.status-err { color: #f87171; }
.modal-footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 10px;
  padding: 16px 24px 20px; border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.btn-cancel {
  padding: 8px 18px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent; color: #64748b; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: color 0.15s, background 0.15s;
}
.btn-cancel:hover { color: #e2e8f0; background: rgba(255, 255, 255, 0.05); }
.btn-save {
  padding: 8px 22px; border-radius: 8px; border: none; background: #6366f1;
  color: #fff; font-size: 13px; font-weight: 700; cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}
.btn-save:hover:not(:disabled) { background: #818cf8; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s ease; }
.modal-fade-enter-active .modal-card, .modal-fade-leave-active .modal-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .modal-card, .modal-fade-leave-to .modal-card {
  transform: translateY(-12px); opacity: 0;
}
</style>
