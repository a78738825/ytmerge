# 🎬 YouTube Downloader CLI (with Stream Selector & Merger)

A Python-based CLI tool that lets you:

✅ Fetch available video & audio streams from a YouTube link  
✅ Choose the quality you want using `itag` values  
✅ Download both streams  
✅ Merge them into a single `.mp4` file using `ffmpeg`  
✅ Clean up temp files after a successful merge

---

## 🚀 Features

- 🎥 Lists all available video & audio streams (with itags, resolutions, and formats)
- 🎛️ Lets you pick the exact quality of video/audio you want to download
- 📥 Downloads and merges streams using `ffmpeg`
- 🧹 Deletes temporary files after merging is complete
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
python main.py
```

You’ll be prompted to:

1. Paste a YouTube video URL 📎
2. View the list of available streams 🧩
3. Select the `itag` for the video 🎥
4. Select the `itag` for the audio 🎵
5. Watch it download, merge and save! 💾

---

## 📁 Output

- Final merged video will be saved as:  
  `"<video-title>.mp4"` (automatically sanitized to be filename-safe)

- Temporary files (`temp_video.*` and `temp_audio.*`) are deleted after merge.

---

## 💡 Notes

- Make sure `ffmpeg` is correctly installed — it’s essential for merging.
- Uses `pytubefix` to avoid issues with the original `pytube` package.
- Not all streams are compatible; in rare cases, merging might fail if formats are too exotic.

---

## 🛠️ To-Do / Future Improvements

> Features to improve and expand this project:

#### 🎯 Core Features

- [ ] Add **audio-only download** option 🎵
- [ ] Show **download progress bar** using `on_progress_callback` and `rich.progress` ⏳
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

Made with ☕, Python, and lots of debug prints.
