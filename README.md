# 🎬 YouTube Downloader CLI (with Stream Selector & Smart Merger)

A Python-based CLI tool that lets you:

✅ Fetch available video & audio streams from a YouTube link  
✅ Choose the quality you want using `itag` values  
✅ Download both streams with progress bars  
✅ Merge them into a `.mp4` or `.webm` file using `ffmpeg` (auto-chosen format)  
✅ Automatically skips re-downloading if files already exist  
✅ Cleans up temp files after a successful merge

---

## 🚀 Features

- 🎥 Lists all available video & audio streams (with itags, resolutions, and formats)
- 🎛️ Lets you pick the exact quality of video/audio you want to download
- 📥 Downloads streams and intelligently merges them using `ffmpeg`
  - Uses stream-copy for `.webm` to avoid re-encoding
  - Re-encodes audio only if necessary
- ⏳ Rich CLI progress bars for video/audio downloads and merge steps
- 🧹 Skips re-downloads for existing temp files and cleans up after merge
- 🖤 Uses `rich` and `tabulate` for clean, readable CLI output

---

## 📦 Requirements

Make sure you have:

- Python 3.8+
- [`ffmpeg`](https://ffmpeg.org/download.html) installed and in your system PATH
- The following Python packages:

```bash
pip install pytubefix rich tabulate
```

---

## 🔧 Usage

```bash
python main.py <YouTube_URL>
```

You’ll be guided to:

1. View the list of available streams 🧩  
2. Select the `itag` for the video 🎥  
3. Select the `itag` for the audio 🎵  
4. Watch it download, merge, and save! 💾

---

## 📁 Output

- Final merged video will be saved as:  
  `"<video-title>.mp4"` or `"<video-title>.webm"`  
  (chosen based on input stream formats, sanitized to be filename-safe)

- Temporary files (`temp_video.*` and `temp_audio.*`) are deleted after merge  
  unless the merge fails or you interrupt with `Ctrl+C`.

---

## 💡 Notes

- Make sure `ffmpeg` is correctly installed — it’s essential for merging.
- Uses `pytubefix` to avoid issues with the original `pytube` package.
- If both streams are `.webm`, merging will use stream-copy for better quality and speed.
- Graceful handling of errors and keyboard interrupts.

---

## 🛠️ To-Do / Future Improvements

> Features to improve and expand this project:

#### 🎯 Core Features

- [ ] Add **audio-only download** option 🎵
- [x] Show **download progress bar** using `on_progress_callback` and `rich.progress` ⏳
- [ ] Let user **choose output filename** or auto-append quality info 📝
- [ ] Add option to **auto-select best quality** (highest res + best audio) 🏆
- [ ] Support for **batch downloading** from multiple URLs 📦

#### ✨ UI/UX Enhancements

- [ ] Switch from `tabulate` to `rich.table` for prettier output 📊
- [ ] Use a **temporary directory** for downloads, auto-cleaned after merging 🧹

#### 💡 Bonus Ideas

- [ ] Allow **caption (subtitle) downloads** if available 📄
- [ ] Save a **download history log** (title, date, quality, etc.) 📘
- [ ] Add **format conversion options** (e.g., `.mp3`, `.mkv`) after merging 🔄

---

## 📸 Preview

> Fancy grid output with video & audio stream listings:

```
🎥 Video Streams:
╒════════╤═════════════╤════════╤═════════════════╕
│ itag   │ resolution  │ type   │ mime_type       │
├────────┼─────────────┼────────┼─────────────────┤
│ 137    │ 1080p       │ video  │ video/mp4       │
│ 136    │ 720p        │ video  │ video/mp4       │
│ 247    │ 720p        │ video  │ video/webm      │
╘════════╧═════════════╧════════╧═════════════════╛

🎵 Audio Streams:
╒════════╤════════╤════════╤═════════════════╕
│ itag   │ type   │ mime_type │ quality       │
├────────┼────────┼───────────┼───────────────┤
│ 140    │ audio  │ audio/mp4 │ 128kbps       │
│ 251    │ audio  │ audio/webm│ 160kbps       │
╘════════╧════════╧═══════════╧═══════════════╛
```

---

## 🧠 Credits

- [pytubefix](https://github.com/Aioloss/pytubefix)
- [ffmpeg](https://ffmpeg.org/)
- [rich](https://github.com/Textualize/rich)
- [tabulate](https://pypi.org/project/tabulate/)

---

## 🖖 License

MIT – use it, share it, break it, build on it.

---

Made with ☕, Python, and a love for clean CLI tools.

