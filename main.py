from pytubefix import YouTube
from rich.console import Console
from tabulate import tabulate
import os
import subprocess
import re
import argparse
import sys
from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    SpinnerColumn,
)

console = Console()


def get_youtube_stream_info(link):
    """
    🔍 Fetches video and audio stream info from the YouTube link.

    Returns:
    - yt object (for later stream retrieval)
    - list of available video streams (dicts)
    - list of available audio streams (dicts)
    - video title
    """
    yt = YouTube(link)
    streams = yt.streams
    title = yt.title

    # 🎧 Filter audio-only streams
    audio_streams = streams.filter(only_audio=True)
    audiosObj = [
        {
            "itag": stream.itag,
            "type": stream.type,
            "mime_type": stream.mime_type,
            "quality": stream.abr,
        }
        for stream in audio_streams
    ]

    # 🎥 Filter streams that have a resolution (i.e., video)
    videosObj = [
        {
            "itag": stream.itag,
            "resolution": stream.resolution,
            "type": stream.type,
            "mime_type": stream.mime_type,
        }
        for stream in streams
        if stream.resolution is not None
    ]

    return yt, videosObj, audiosObj, title


def display_streams(videos, audios):
    """
    🧾 Prints available video & audio stream options in fancy tables.
    """
    print("🎥 Video Streams:")
    print(tabulate(videos, headers="keys", tablefmt="fancy_grid"))

    print("🎵 Audio Streams:")
    print(tabulate(audios, headers="keys", tablefmt="fancy_grid"))


def select_stream(yt, *_):
    """
    🎯 Prompts user to select desired itags for video & audio.
    Fetches corresponding stream objects and returns them.
    """
    video_itag = console.input(
        "[bold cyan]Enter the itag of the video quality you want to download:[/bold cyan] "
    )
    video_stream = yt.streams.get_by_itag(int(video_itag))

    audio_itag = console.input(
        "[bold cyan]Enter the itag of the audio quality you want to download:[/bold cyan] "
    )
    audio_stream = yt.streams.get_by_itag(int(audio_itag))

    return video_stream, audio_stream


def download_streams(video_stream, audio_stream):
    """
    ⬇️ Downloads the selected video and audio streams.
    🧠 Uses rich progress bars and dynamically handles MIME-based extensions.
    📦 Returns paths to the downloaded files.
    """
    console.print(
        "\n[bold green]📥 Starting download of selected streams...[/bold green]"
    )

    # 🔍 Extract file extensions (e.g., mp4, webm)
    video_ext = video_stream.mime_type.split("/")[-1]
    audio_ext = audio_stream.mime_type.split("/")[-1]

    # 📝 Define temp filenames using actual extensions
    video_path = f"temp_video.{video_ext}"
    audio_path = f"temp_audio.{audio_ext}"

    # 👀 Show the formats being downloaded
    console.print(f"[dim]Video format: .{video_ext}, Audio format: .{audio_ext}[/dim]")

    # Download video with separate progress bar
    with Progress(
        SpinnerColumn(style="bold cyan"),
        TextColumn("[bold white]{task.description}"),
        BarColumn(bar_width=None),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        task_id = progress.add_task(
            "🎥 Downloading video...", total=video_stream.filesize
        )

        def video_progress(stream, chunk, bytes_remaining):
            downloaded = stream.filesize - bytes_remaining
            progress.update(task_id, completed=downloaded)

        # Attach callback and download
        video = yt.streams.get_by_itag(video_stream.itag)
        if (
            not os.path.exists(video_path) and video is not None
        ):  # 🧠 Skip download if file already exists AND if the stream itag is valid
            yt.register_on_progress_callback(video_progress)
            video.download(filename=video_path)
        else:
            console.print(
                f"[yellow]⚠️ Skipping video download, file already exists: {video_path}[/yellow]"
            )

    # Download audio with a new progress bar
    with Progress(
        SpinnerColumn(style="bold magenta"),
        TextColumn("[bold white]{task.description}"),
        BarColumn(bar_width=None),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        task_id = progress.add_task(
            "🎵 Downloading audio...", total=audio_stream.filesize
        )

        def audio_progress(stream, chunk, bytes_remaining):
            downloaded = stream.filesize - bytes_remaining
            progress.update(task_id, completed=downloaded)

        # Attach callback and download
        audio = yt.streams.get_by_itag(audio_stream.itag)
        if (
            not os.path.exists(audio_path) and audio is not None
        ):  # 🧠 Skip download if file already exists AND if the stream itag is valid
            yt.register_on_progress_callback(audio_progress)
            audio.download(filename=audio_path)
        else:
            console.print(
                f"[yellow]⚠️ Skipping audio download, file already exists: {audio_path}[/yellow]"
            )

    console.print("[bold green]✅ Download complete![/bold green]\n")

    return video_path, audio_path


def get_duration(path):
    """Return duration of a media file in seconds using ffprobe."""
    import subprocess
    import json

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        return float(json.loads(result.stdout)["format"]["duration"])
    except Exception:
        return None


def merge_streams(video_path, audio_path, title):
    """
    🎞️ Merges the video and audio files using ffmpeg.
    🧼 Sanitizes title for the final filename.
    ✅ Returns success status.
    """
    console.print("[bold yellow]Merging video and audio...[/bold yellow]")

    # 🧼 Sanitize the title to create a safe filename
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
    output_path = f"{safe_title}.mp4"

    total_duration = get_duration(video_path)
    if not total_duration:
        console.print(
            "[bold red]⚠ Could not determine duration for merge progress bar.[/bold red]"
        )
        total_duration = 100  # Fallback

    # 🛠️ ffmpeg command to merge video & audio
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-strict",
        "experimental",
        "-y",  # overwrite output file without asking
        "-progress",
        "-",  # Enable live progress output to stdout
        output_path,
    ]

    # 🧪Progress Bar
    with Progress(
        SpinnerColumn(style="bold green"),
        TextColumn("[bold white]{task.description}"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        task_id = progress.add_task("🔧 Merging...", total=total_duration)

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        if process.stdout is not None:
            for line in process.stdout:
                if "out_time_ms=" in line:
                    match = re.search(r"out_time_ms=(\d+)", line)
                    if match:
                        current_ms = int(match.group(1))
                        current_sec = current_ms / 1_000_000
                        progress.update(task_id, completed=current_sec)
        else:
            console.print(
                "[bold red]⚠ ffmpeg did not return a readable stdout stream.[/bold red]"
            )

        process.wait()

    if process.returncode == 0:
        console.print(
            f"[bold green]✅ Merge complete! Saved as [underline]{output_path}[/underline][/bold green]"
        )
        return True
    else:
        console.print("[bold red]❌ Merge failed![/bold red]")
        return False


def cleanup(*files):
    """
    🧹 Deletes temporary files (e.g., downloaded video/audio).
    """
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            console.print(f"[dim]Deleted temp file: {file}[/dim]")


def parse_args():
    parser = argparse.ArgumentParser(
        description="🎬 YouTube downloader with stream selection, merging, and rich progress bars."
    )
    parser.add_argument("url", help="YouTube video URL")
    return parser.parse_args()


# 🧠 Main program
if __name__ == "__main__":
    args = parse_args()

    try:
        # 🔗 Ask user for the YouTube link
        link = args.url

        # 📡 Fetch available streams and video title
        yt, videos, audios, title = get_youtube_stream_info(link)

        # 🖼️ Show title
        console.print(f"Title: {title}", style="bold green")

        if not videos or not audios:
            console.print("[bold red]❌ No streams found.[/bold red]")
            sys.exit(1)

        # 📊 Show available streams
        display_streams(videos, audios)

        # 🎯 Prompt user for selections
        video_stream, audio_stream = select_stream(yt, videos, audios)

        # ⬇️ Download and 🎞️ Merge
        video_path, audio_path = download_streams(video_stream, audio_stream)
        success = merge_streams(video_path, audio_path, title)

        # 🧹 Cleanup temp files if all good
        if success:
            cleanup(video_path, audio_path)

    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C
        # Show exit message, clean up temp files if any exist
        # Ignore cleanup errors and exit with code 1 (user interruption)

        console.print(
            "\n[bold red]⛔ Interrupted by user. Exiting safely...[/bold red]"
        )
        try:
            # Try cleaning up temp files — if they exist
            cleanup("temp_video.mp4", "temp_audio.mp4")
        except Exception:
            pass  # Ignore errors like missing files or permission issues
        sys.exit(1)
