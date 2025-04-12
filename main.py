from pytubefix import YouTube
from rich.console import Console

# from rich.table import Table
import pandas as pd
from tabulate import tabulate

console = Console()


def get_youtube_stream_info(link):
    # todo :
    # 1. add progress bar using on_progress_callback argument that can be given to streams object

    yt = YouTube(link)
    streams = yt.streams
    title = yt.title
    # caption = yt.captions

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
    Prints a formatted table of available video and audio streams.
    Does not return anything.
    """

    print("🎥 Video Streams:")
    print(tabulate(videos, headers="keys", tablefmt="fancy_grid"))

    print("🎵 Audio Streams:")
    print(tabulate(audios, headers="keys", tablefmt="fancy_grid"))


def select_stream(yt, video_itag, audio_itag):
    video_itag = console.input(
        "[bold cyan]Enter the itag of the video quality you want to download:[/bold cyan] "
    )
    video_stream = yt.streams.get_by_itag(int(video_itag))

    audio_itag = console.input(
        "[bold cyan]Enter the itag of the audio quality you want to download:[/bold cyan] "
    )
    audio_stream = yt.streams.get_by_itag(int(audio_itag))

    return video_stream, audio_stream


import os


def download_streams(video_stream, audio_stream):
    console.print("\n[bold green]Downloading streams...[/bold green]")

    # 🔍 Get file extensions from MIME types (e.g. "video/mp4" -> "mp4")
    video_ext = video_stream.mime_type.split("/")[1]
    audio_ext = audio_stream.mime_type.split("/")[1]

    # 📝 Define temp filenames with correct extensions
    video_path = f"temp_video.{video_ext}"
    audio_path = f"temp_audio.{audio_ext}"

    # 📢 Show user the formats being downloaded
    console.print(
        f"Video format: .{video_ext}, Audio format: .{audio_ext}", style="dim"
    )

    # 📥 Download the streams to temp files
    video_stream.download(filename=video_path)
    audio_stream.download(filename=audio_path)

    # 🔙 Return the paths for further processing (like merging)
    return video_path, audio_path


import subprocess


def merge_streams(video_path, audio_path, title):
    console.print("[bold yellow]Merging video and audio...[/bold yellow]")

    # sanitize title for file name
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
    output_path = f"{safe_title}.mp4"

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
        "-y",  # overwrite without asking
    ]

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
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            console.print(f"[dim]Deleted temp file: {file}[/dim]")


if __name__ == "__main__":
    link = console.input("Enter the YouTube video URL: ")

    # Get available streams
    yt, videos, audios, title = get_youtube_stream_info(link)

    # Display title
    console.print(f"Title: {title}", style="bold green")

    if videos and audios:
        display_streams(videos, audios)
        video_stream, audio_stream = select_stream(yt, videos, audios)

        video_path, audio_path = download_streams(video_stream, audio_stream)
        success = merge_streams(video_path, audio_path, title)

        if success:
            cleanup(video_path, audio_path)
    else:
        print("⚠️  Couldn’t find video or audio streams for this link.")
