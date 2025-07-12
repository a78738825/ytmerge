import json
import os
import re
import subprocess

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

console = Console()


def get_duration(path):
    """Return duration of a media file in seconds using ffprobe."""

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
    # TODO - Make it so that if the extensions of both audio and video are matched, there is no re-encoding [like i did for webm]
    console.print("[bold yellow]Merging video and audio...[/bold yellow]")

    # 🧼 Sanitize the title to create a safe filename
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()

    # If Both the audio and video are webm format merge them to webm too; otherwise into mp4
    video_ext = os.path.splitext(video_path)[1]
    audio_ext = os.path.splitext(audio_path)[1]
    if video_ext == ".webm" and audio_ext == ".webm":
        output_ext = ".webm"
        copy_both = True
    elif video_ext == ".mp4" and audio_ext == ".mp4":
        output_ext = ".mp4"
        copy_both = True
    else:
        output_ext = ".mp4"
        copy_both = False

    output_path = f"{safe_title}{output_ext}"

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
        # 🧠 Use stream copy for video — always copy since we don't re-encode video
        "-c:v",
        "copy",
        # 🎵 Use stream copy for audio *only if both streams have the same compatible format*
        # Otherwise, re-encode audio to AAC (for compatibility with .mp4)
        "-c:a",
        "copy" if copy_both else "aac",
    ]

    # 🎚️ Only set audio bitrate if re-encoding (AAC)
    if not copy_both:
        command += ["-b:a", "192k"]  # Skipping this avoids errors with stream copy

    # ⏱️ Stop encoding when the shorter stream ends (helps avoid desync)
    # 📢 Overwrite output file if it exists
    # 📊 Enable ffmpeg progress output to stdout
    # 🧾 Output file path (webm or mp4 depending on codec match)
    command += [
        "-shortest",
        "-y",
        "-progress",
        "-",
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
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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
        # Debug ffmpeg merging errors
        # if process.stderr:
        #     error_output = process.stderr.read()
        #     console.print(f"[red]{error_output}[/red]")
        # else:
        #     console.print("[dim]No error message captured from ffmpeg.[/dim]")
        # Debug ends
        return False
