
# Changelog

All notable changes to this project will be documented in this file.

---

## [0.5.0] – 2025-04-16
### Added
- Switched to `argparse` for argument parsing
- Skips existing temp files to avoid redownloading
- Graceful exits on Ctrl+C with cleanup

### Fixed
- Replaced unsafe `except:` blocks with specific error handling

---

## [0.4.0] – 2025-04-14
### Added
- Real-time merge progress bar using Rich
- Duration and ETA feedback during ffmpeg merge

---

## [0.3.1] – 2025-04-14
### Fixed
- Progress bar logic for downloads
- Removed invalid `.watch_url` access
- Used local progress callbacks for each stream

---

## [0.3.0] – 2025-04-12
### Added
- Rich progress bar for downloads (video & audio)
- Speed, time remaining, and fancy visuals

---

## [0.2.0] – 2025-04-12
### Added
- README file
- Minimal progress indicator

---

## [0.1.0] – 2025-04-12
### Added
- Core YouTube downloader: stream selection, download, and merging
