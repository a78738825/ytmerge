import os

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

console = Console()


def download_streams(video_stream, audio_stream, yt):
    """
    ⬇️ Downloads the selected video and audio streams.
    🧠 Uses rich progress bars and dynamically handles MIME-based extensions.
    📦 Returns paths to the downloaded files.
    """
    console.print(
        "\n[bold green]📥 Starting download of selected streams...[/bold green]"
    )

    video_path = None
    audio_path = None

    if video_stream is not None:
        # 🔍 Extract file extensions (e.g., mp4, webm)
        video_ext = video_stream.mime_type.split("/")[-1]

        # 📝 Define temp filename using actual extensions
        video_path = f"temp_video.{video_ext}"

        # 👀 Show the format being downloaded
        console.print(f"[dim]Video format: .{video_ext}[/dim]")

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

    # 🔍 Extract file extensions (e.g., mp4, webm)
    audio_ext = audio_stream.mime_type.split("/")[-1]

    # 📝 Define temp filename using actual extensions
    audio_path = f"temp_audio.{audio_ext}"

    # 👀 Show the format being downloaded
    console.print(f"[dim]Audio format: .{audio_ext}[/dim]")

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
