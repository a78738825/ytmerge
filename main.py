import os
import sys
from urllib.error import URLError

from pytubefix.exceptions import PytubeFixError
from rich.console import Console

from cli import parse_args
from downloader import download_streams
from logger import logger
from merger import merge_streams
from streams import StreamSelector
from utils import cleanup

console = Console()

# 🧠 Main program
if __name__ == "__main__":
    args = parse_args()

    try:
        # 🔗 Ask user for the YouTube link
        link = args.url

        # 📡 Fetch available streams and video title
        try:
            # 🎛️ Initialize stream stream_handler (handles fetching info + user selection)
            stream_handler = StreamSelector(link)
            logger.info(f"Fetched Youtube Video: {stream_handler.title} => [ {link} ]")
        except (PytubeFixError, URLError, ConnectionError) as retrieval_error:
            console.print(
                f"[bold red]📡 Network or retrieval error:[/bold red] {str(retrieval_error)}"
            )
            sys.exit(1)

        # 🖼️ Show title
        console.rule("[bold blue] Video Information [/bold blue]")
        console.print(f"Title: {stream_handler.title}", style="bold green")
        print("\n")

        if not stream_handler.videos and not stream_handler.audios:
            console.print("[bold red]❌ No streams found.[/bold red]")
            sys.exit(1)

        # 📊 Show available streams
        stream_handler.display_streams(audio_only=args.audio_only)

        # 🎯 Prompt user for selections (audio-only or both video+audio)
        video_stream, audio_stream = stream_handler.select_streams(
            audio_only=args.audio_only
        )

        # 🧾 Log selections
        if video_stream:
            logger.info(
                "User selected video itag: %s (%s, %s)",
                video_stream.itag,
                video_stream.resolution,
                video_stream.mime_type,
            )
            logger.info("Video size: %.2f MB", video_stream.filesize / 1024 / 1024)

        if audio_stream:
            logger.info(
                "User selected audio itag: %s (%s, %s)",
                audio_stream.itag,
                audio_stream.abr,
                audio_stream.mime_type,
            )
            logger.info("Audio size: %.2f MB", audio_stream.filesize / 1024 / 1024)

        # ⬇️ Download
        try:
            video_path, audio_path = download_streams(
                video_stream, audio_stream, stream_handler.yt
            )
        except Exception as download_error:
            console.print(
                f"[bold red]💾 Download error:[/bold red] {str(download_error)}"
            )
            sys.exit(1)

        # 🎞️ Merge
        if video_stream:
            try:
                success = merge_streams(video_path, audio_path, stream_handler.title)
                # 🧹 Cleanup temp files if all good
                if success:
                    cleanup(video_path, audio_path)
                    logger.info("✅ Merge successful: %s", stream_handler.title)
            except Exception as ffmpeg_error:
                logger.error("❌ Merge failed: %s", stream_handler.title)
                console.print(
                    f"[bold red]🎞️ Merge error:[/bold red] {str(ffmpeg_error)}"
                )
                sys.exit(1)
        else:
            # 🎧 Audio-only: Rename temp file to match video title
            console.print(
                f"[bold green]✅ Audio-only download complete: {audio_path}[/bold green]"
            )

            if audio_path:
                # 🧼 Sanitize title for final filename
                sanitized_title = "".join(
                    c for c in stream_handler.title if c.isalnum() or c in " _-"
                ).rstrip()

                final_audio_path = f"{sanitized_title}{os.path.splitext(audio_path)[1]}"
                logger.info(
                    "Renaming audio file: %s → %s", audio_path, final_audio_path
                )
                os.rename(audio_path, final_audio_path)

                logger.info("✅ Audio-only file saved as: %s", final_audio_path)
                console.print(
                    f"[bold green]🎧 Renamed to: [underline]{final_audio_path}[/underline][/bold green]"
                )

    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C
        # Show exit message, clean up temp files if any exist
        # Ignore cleanup errors and exit with code 1 (user interruption)

        console.print(
            "\n[bold red]⛔ Interrupted by user. Exiting safely...[/bold red]"
        )
        try:
            # Try cleaning up temp files — if they exist
            cleanup(
                (
                    video_path
                    if "video_path" in locals() and video_path
                    else "temp_video.mp4"
                ),
                (
                    audio_path
                    if "audio_path" in locals() and audio_path
                    else "temp_audio.mp4"
                ),
            )
        except Exception as KI:
            # pass  # Ignore errors like missing files or permission issues
            logger.warning(f"Cleanup Failed: {KI}")
        sys.exit(1)
