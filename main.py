from .streams import get_youtube_stream_info, display_streams, select_stream
from .downloader import download_streams
from .merger import merge_streams

from .cli import parse_args
from .utils import cleanup

from rich.console import Console
from pytubefix.exceptions import PytubeFixError
from urllib.error import URLError
import sys

console = Console()

# 🧠 Main program
if __name__ == "__main__":
    args = parse_args()

    try:
        # 🔗 Ask user for the YouTube link
        link = args.url

        # 📡 Fetch available streams and video title
        try:
            yt, videos, audios, title = get_youtube_stream_info(link)
        except (PytubeFixError, URLError, ConnectionError) as retrieval_error:
            console.print(
                f"[bold red]📡 Network or retrieval error:[/bold red] {str(retrieval_error)}"
            )
            sys.exit(1)

        # 🖼️ Show title
        console.print(f"Title: {title}", style="bold green")

        if not videos or not audios:
            console.print("[bold red]❌ No streams found.[/bold red]")
            sys.exit(1)

        # 📊 Show available streams
        display_streams(videos, audios)

        # 🎯 Prompt user for selections
        video_stream, audio_stream = select_stream(yt, videos, audios)

        # ⬇️ Download
        try:
            video_path, audio_path = download_streams(video_stream, audio_stream, yt)
        except Exception as download_error:
            console.print(
                f"[bold red]💾 Download error:[/bold red] {str(download_error)}"
            )
            sys.exit(1)

        # 🎞️ Merge
        try:
            success = merge_streams(video_path, audio_path, title)
            # 🧹 Cleanup temp files if all good
            if success:
                cleanup(video_path, audio_path)
        except Exception as ffmpeg_error:
            console.print(f"[bold red]🎞️ Merge error:[/bold red] {str(ffmpeg_error)}")
            sys.exit(1)

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
