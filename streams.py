from pytubefix import YouTube
from rich.console import Console
from tabulate import tabulate

console = Console()


class StreamSelector:
    """
    🎛️ StreamSelector handles fetching, displaying, and selecting video/audio streams from a YouTube link.

    Responsibilities:
    - Fetch available streams
    - Display streams in fancy tables (video, audio, or both)
    - Prompt user for stream selections (video+audio or audio-only)
    """

    def __init__(self, link):
        """
        Initializes the StreamSelector object by fetching YouTube stream data.

        Parameters:
        - link (str): YouTube video URL

        Attributes:
        - yt (YouTube): pytubefix YouTube object
        - videos (list): List of available video stream info (dicts)
        - audios (list): List of available audio stream info (dicts)
        - title (str): Video title
        """
        self.yt = YouTube(link)
        self.title = self.yt.title
        streams = self.yt.streams

        # 🎧 Filter audio-only streams
        audio_streams = streams.filter(only_audio=True)
        self.audios = [
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
        self.videos = [
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

    def display_streams(self, audio_only=False):
        """
        🧾 Prints available video & audio stream options in fancy tables.

        Parameters:
        - audio_only (bool): If True, displays only audio streams. Otherwise, displays both video and audio.
        """
        if not audio_only:
            print("🎥 Video Streams:")
            print(tabulate(self.videos, headers="keys", tablefmt="fancy_grid"))

        print("🎵 Audio Streams:")
        print(tabulate(self.audios, headers="keys", tablefmt="fancy_grid"))

    def select_streams(self, audio_only=False):
        """
        🎯 Prompts user to select desired itags for video & audio.

        Parameters:
        - audio_only (bool): If True, prompts only for audio stream selection.

        Returns:
        - (video_stream, audio_stream): Tuple of pytubefix stream objects.
          If audio_only is True, video_stream is returned as None.
        """
        if not audio_only:
            video_itag = console.input(
                "[bold cyan]Enter the itag of the video quality you want to download:[/bold cyan] "
            )
            video_stream = self.yt.streams.get_by_itag(int(video_itag))
        else:
            video_stream = None

        audio_itag = console.input(
            "[bold cyan]Enter the itag of the audio quality you want to download:[/bold cyan] "
        )
        audio_stream = self.yt.streams.get_by_itag(int(audio_itag))

        return video_stream, audio_stream
