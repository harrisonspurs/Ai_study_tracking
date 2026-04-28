# utility functions for the app


def format_time(seconds):
    # convert seconds to MM:SS format
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"
