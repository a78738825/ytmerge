import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="🎬 YouTube downloader with stream selection, merging, and rich progress bars."
    )
    parser.add_argument("url", help="YouTube video URL")
    return parser.parse_args()
