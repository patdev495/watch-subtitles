# Watch Subtitles

Ứng dụng desktop để xem video với phụ đề và các dịch vụ dịch thuật.

## Phát triển trên máy khác

Yêu cầu: Git, [Node.js](https://nodejs.org/) với PNPM, và [uv](https://docs.astral.sh/uv/).

```powershell
git clone https://github.com/patdev495/watch-subtitles.git
cd watch-subtitles
uv sync
pnpm --dir frontend install --frozen-lockfile
```

Để chạy ở chế độ phát triển, mở hai terminal:

```powershell
# Terminal 1: giao diện Vue/Vite
pnpm --dir frontend dev
```

```powershell
# Terminal 2: ứng dụng desktop
uv run python main.py --dev
```

Trước khi bắt đầu làm việc trên một máy khác, đồng bộ mã nguồn:

```powershell
git pull origin master
```

Sau khi hoàn thành thay đổi, chỉ thêm các file mã nguồn cần thiết rồi commit và push:

```powershell
git add <file-hoac-thu-muc>
git commit -m "mo ta thay doi"
git push origin master
```

Không commit `node_modules/`, `.venv/`, `frontend/dist/`, hoặc thư mục build. Các thư mục này được tạo lại từ các lệnh ở trên.

## Build file EXE duy nhất (Windows)

Script build tạo `dist/watch-subtitles.exe`, đóng gói cả giao diện đã build và FFmpeg vào một file thực thi. Máy đích không cần cài FFmpeg riêng.

```powershell
.\scripts\build-exe.ps1
```

Script sẽ cài dependencies frontend theo lockfile, chạy kiểm tra kiểu và build Vue, sau đó dùng PyInstaller qua `uv`. Có thể chỉ định tên output khác:

```powershell
.\scripts\build-exe.ps1 -Name "WatchSubtitles"
```

Lần chạy đầu cần kết nối Internet để `uv` tải PyInstaller. Máy build cần có FFmpeg trong `PATH`, hoặc đặt biến môi trường `FFMPEG_PATH` trỏ đến `ffmpeg.exe`. Khi chạy file `.exe`, PyInstaller sẽ giải nén các tài nguyên tạm thời trước khi mở ứng dụng.
