import type { Cue } from '../types';

export const MOCK_LINES: [string, string][] = [
  ['Hello, welcome to the video player.', 'Xin chào, chào mừng đến với trình phát video.'],
  ['This is a demonstration of the bilingual transcript footer.', 'Đây là bản demo của thanh phụ đề song ngữ.'],
  ['Each cue displays the original and translated text.', 'Mỗi dòng cue hiển thị văn bản gốc và bản dịch.'],
  ['Click any cue to seek the video to that moment.', 'Nhấp vào bất kỳ cue nào để tua video đến thời điểm đó.'],
  ['The active cue is highlighted automatically.', 'Cue đang phát được tô sáng tự động.'],
  ['Auto-scroll keeps the active cue in view.', 'Cuộn tự động giữ cue đang phát trong tầm nhìn.'],
  ['You can also drag and drop a video file onto this window.', 'Bạn cũng có thể kéo thả tệp video vào cửa sổ này.'],
  ['The backend is powered by Python with UV.', 'Backend được chạy bằng Python với UV.'],
  ['Deepgram handles speech-to-text transcription.', 'Deepgram xử lý chuyển đổi giọng nói thành văn bản.'],
  ['DeepL handles bilingual translation.', 'DeepL xử lý dịch song ngữ.'],
  ['Configure your API keys in Settings.', 'Cấu hình API key của bạn trong Cài đặt.'],
  ['The app will cache subtitles by video fingerprint.', 'Ứng dụng sẽ cache phụ đề theo video fingerprint.'],
  ["You won't be charged twice for the same video.", 'Bạn sẽ không bị tính phí hai lần cho cùng một video.'],
  ['Subtitles can be exported as .srt or .vtt files.', 'Phụ đề có thể xuất ra dưới dạng .srt hoặc .vtt.'],
  ['The transcript is fully interactive.', 'Bản ghi là hoàn toàn tương tác.'],
  ['Seek precisely by clicking any cue.', 'Tua chính xác bằng cách nhấp vào bất kỳ cue nào.'],
];

export function getMockCues(): Cue[] {
  return MOCK_LINES.map((pair, i) => ({
    id: String(i + 1),
    start: i * 4,
    end: (i + 1) * 4,
    originalText: pair[0],
    translatedText: pair[1],
  }));
}
