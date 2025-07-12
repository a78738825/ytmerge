import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="🎬 YouTube downloader with stream selection, merging, and rich progress bars."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Download audio stream only (no video)",
    )
    return parser.parse_args()
