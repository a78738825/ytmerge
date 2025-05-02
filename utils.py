import os
from rich.console import Console


console = Console()


def cleanup(*files):
    """
    🧹 Deletes temporary files (e.g., downloaded video/audio).
    """
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            console.print(f"[dim]Deleted temp file: {file}[/dim]")
