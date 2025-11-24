#!/usr/bin/env python3
"""
Test encoding with different H.264 settings to find WeChat-compatible format
"""

import subprocess
import os

# Test video
original_video = "/Users/linzhu/Documents/Project/z2/storage/videos/2025-10/uhJJgc-0iTQ.mp4"
test_srt = "/Users/linzhu/Documents/Project/z2/storage/subtitles/2025-10/uhJJgc-0iTQ_zh.srt"
output_dir = "/Users/linzhu/Documents/Project/z2/storage/videos/2025-10"

# Encoding tests
tests = [
    {
        "name": "baseline_31",
        "params": {
            'profile:v': 'baseline',
            'level': '3.1',
            'pix_fmt': 'yuv420p',
            'preset': 'medium',
            'crf': '23',
            'movflags': '+faststart'
        }
    },
    {
        "name": "main_40",
        "params": {
            'profile:v': 'main',
            'level': '4.0',
            'pix_fmt': 'yuv420p',
            'preset': 'medium',
            'crf': '23',
            'movflags': '+faststart'
        }
    },
    {
        "name": "high_42_nolimit",
        "params": {
            'profile:v': 'high',
            'level': '4.2',
            'pix_fmt': 'yuv420p',
            'preset': 'medium',
            'crf': '23',
            'movflags': '+faststart'
            # No maxrate/bufsize
        }
    },
    {
        "name": "copy_codec",
        "params": None  # Special: just copy video codec without re-encoding
    }
]

for test in tests:
    print(f"\n{'='*60}")
    print(f"Testing: {test['name']}")
    print(f"{'='*60}")

    output_file = os.path.join(output_dir, f"test_{test['name']}.mp4")

    if test['params'] is None:
        # Try copying video codec
        cmd = [
            'ffmpeg', '-y', '-i', original_video,
            '-vf', f"subtitles={test_srt}",
            '-c:v', 'libx264',  # Still need to re-encode because of subtitle filter
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-movflags', '+faststart',
            output_file
        ]
    else:
        cmd = [
            'ffmpeg', '-y', '-i', original_video,
            '-vf', f"subtitles={test_srt}",
            '-c:v', 'libx264',
            '-c:a', 'aac'
        ]
        for key, value in test['params'].items():
            if ':' in key:
                cmd.extend([f'-{key}', value])
            else:
                cmd.extend([f'-{key}', value])
        cmd.append(output_file)

    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Check the output
        probe_cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,profile,level,bit_rate',
            '-of', 'default=noprint_wrappers=1',
            output_file
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        print(f"\n✓ Success! Output info:")
        print(probe_result.stdout)
        print(f"File: {output_file}")
    else:
        print(f"\n✗ Failed!")
        print(result.stderr[:500])

print(f"\n{'='*60}")
print("Testing complete!")
print(f"Test files created in: {output_dir}")
print("Please test each file with WeChat upload")
print(f"{'='*60}")
