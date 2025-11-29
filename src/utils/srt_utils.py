"""
SRT subtitle file utilities
"""

import pysrt
from typing import List, Dict, Tuple
from datetime import timedelta


def seconds_to_srt_time(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)

    Args:
        seconds: Time in seconds

    Returns:
        SRT formatted timestamp string
    """
    # Round to nearest millisecond to avoid floating-point precision issues
    total_millis = round(seconds * 1000)

    hours = total_millis // 3600000
    remaining = total_millis % 3600000
    minutes = remaining // 60000
    remaining = remaining % 60000
    secs = remaining // 1000
    millis = remaining % 1000

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def srt_time_to_seconds(srt_time: str) -> float:
    """
    Convert SRT timestamp to seconds

    Args:
        srt_time: SRT formatted timestamp (HH:MM:SS,mmm)

    Returns:
        Time in seconds
    """
    time_part, millis = srt_time.replace(',', '.').rsplit('.', 1)
    h, m, s = map(int, time_part.split(':'))
    total_seconds = h * 3600 + m * 60 + s + int(millis) / 1000
    return total_seconds


def create_srt_file(segments: List[Dict], output_path: str) -> None:
    """
    Create an SRT file from subtitle segments

    Args:
        segments: List of subtitle segments with start, end, and text
        output_path: Path to output SRT file
    """
    subs = pysrt.SubRipFile()

    for i, segment in enumerate(segments, start=1):
        start_time = seconds_to_srt_time(segment['start'])
        end_time = seconds_to_srt_time(segment['end'])
        text = segment['text']

        sub = pysrt.SubRipItem(
            index=i,
            start=start_time,
            end=end_time,
            text=text
        )
        subs.append(sub)

    subs.save(output_path, encoding='utf-8')


def read_srt_file(srt_path: str) -> List[Dict]:
    """
    Read an SRT file and return segments

    Args:
        srt_path: Path to SRT file

    Returns:
        List of segments with start, end, and text
    """
    subs = pysrt.open(srt_path, encoding='utf-8')

    segments = []
    for sub in subs:
        segments.append({
            'index': sub.index,
            'start': srt_time_to_seconds(str(sub.start)),
            'end': srt_time_to_seconds(str(sub.end)),
            'start_time': str(sub.start),
            'end_time': str(sub.end),
            'text': sub.text
        })

    return segments


def validate_srt_file(srt_path: str) -> Tuple[bool, str]:
    """
    Validate an SRT file

    Args:
        srt_path: Path to SRT file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        subs = pysrt.open(srt_path, encoding='utf-8')

        if len(subs) == 0:
            return False, "SRT file is empty"

        # Check for sequential indices
        for i, sub in enumerate(subs, start=1):
            if sub.index != i:
                return False, f"Non-sequential index at position {i}"

        # Check for valid timestamps
        for sub in subs:
            if sub.start >= sub.end:
                return False, f"Invalid timestamp in subtitle {sub.index}"

        return True, "Valid SRT file"

    except Exception as e:
        return False, f"Error reading SRT file: {str(e)}"


def split_long_subtitle(text: str, max_chars: int = 42) -> List[str]:
    """
    Split a long subtitle text into multiple lines

    Args:
        text: Subtitle text
        max_chars: Maximum characters per line

    Returns:
        List of text lines
    """
    if len(text) <= max_chars:
        return [text]

    # Try to split at spaces
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines
