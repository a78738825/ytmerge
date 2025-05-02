from pytubefix import YouTube
from tabulate import tabulate
from rich.console import Console

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
            # "filesize": Convert the stream's file size from bytes to megabytes by dividing by 1024 twice (bytes → KB → MB),
            # then convert to string, slice to keep only the first 5 characters for brevity (e.g., "3.57 "), and append " MB"
            "filesize": str(stream.filesize / 1024 / 1024)[:5] + " MB",
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
            # "filesize": Convert the stream's file size from bytes to megabytes by dividing by 1024 twice (bytes → KB → MB),
            # then convert to string, slice to keep only the first 5 characters for brevity (e.g., "3.57 "), and append " MB"
            "filesize": str(stream.filesize / 1024 / 1024)[:5] + " MB",
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
