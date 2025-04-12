from pytubefix import YouTube
from rich.console import Console
from rich.progress import Progress, BarColumn, DownloadColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from tabulate import tabulate
import os
import subprocess

console = Console()

progress_bar = None
progress_task = None

def on_progress(stream, chunk, bytes_remaining):
    global progress_bar, progress_task
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining

    if progress_bar and progress_task:
        progress_bar.update(progress_task, completed=bytes_downloaded)


def get_youtube_stream_info(link):
    """
    🔍 Fetches video and audio stream info from the YouTube link.

    Returns:
    - yt object (for later stream retrieval)
    - list of available video streams (dicts)
    - list of available audio streams (dicts)
    - video title
    """
    yt = YouTube(link, on_progress_callback=on_progress)
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
    🧠 Determines file extensions automatically from MIME types.
    📦 Returns paths to the downloaded files.
    """
    console.print("\n[bold green]Downloading streams...[/bold green]")

    # 🔍 Extract file extensions (e.g., mp4, webm)
    video_ext = video_stream.mime_type.split("/")[1]
    audio_ext = audio_stream.mime_type.split("/")[1]

    # 📝 Define temp filenames using actual extensions
    video_path = f"temp_video.{video_ext}"
    audio_path = f"temp_audio.{audio_ext}"

    # 👀 Show the formats being downloaded
    console.print(
        f"Video format: .{video_ext}, Audio format: .{audio_ext}", style="dim"
    )

    # 🚀 Perform downloads
    global progress_bar, progress_task

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        progress_bar = progress

        # Download video
        progress_task = progress.add_task("[cyan]Downloading video...", total=video_stream.filesize)
        video_stream.download(filename=video_path)

        # Download audio
        progress_task = progress.add_task("[magenta]Downloading audio...", total=audio_stream.filesize)
        audio_stream.download(filename=audio_path)

    return video_path, audio_path


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
        output_path,
        "-y",  # overwrite output file without asking
    ]

    # 🧪 Run ffmpeg
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        console.print(
            f"[bold green]✅ Merge complete! Saved as [underline]{output_path}[/underline][/bold green]"
        )
        return True
    else:
        console.print("[bold red]❌ Merge failed![/bold red]")
        console.print(result.stderr.decode())
        return False


def cleanup(*files):
    """
    🧹 Deletes temporary files (e.g., downloaded video/audio).
    """
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            console.print(f"[dim]Deleted temp file: {file}[/dim]")


# 🧠 Main program
if __name__ == "__main__":
    # 🔗 Ask user for the YouTube link
    link = console.input("Enter the YouTube video URL: ")

    # 📡 Fetch available streams and video title
    yt, videos, audios, title = get_youtube_stream_info(link)

    # 🖼️ Show title
    console.print(f"Title: {title}", style="bold green")

    if videos and audios:
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
    else:
        console.print(
            "⚠️  Couldn’t find video or audio streams for this link.", style="bold red"
        )
