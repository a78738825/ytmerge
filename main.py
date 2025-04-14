from pytubefix import YouTube
from rich.console import Console
from tabulate import tabulate
import os
import subprocess
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
        if not os.path.exists(video_path):
            yt.register_on_progress_callback(video_progress)
            yt.streams.get_by_itag(video_stream.itag).download(filename=video_path)
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
        if not os.path.exists(audio_path):
            yt.register_on_progress_callback(audio_progress)
            yt.streams.get_by_itag(audio_stream.itag).download(filename=audio_path)
        else:
            console.print(
                f"[yellow]⚠️ Skipping audio download, file already exists: {audio_path}[/yellow]"
            )

    console.print("[bold green]✅ Download complete![/bold green]\n")

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
