#!/usr/bin/env python3
"""
Script to re-upload a processed video to WeChat
Usage: python reupload_video.py
"""

from src.publisher import Publisher
from src.storage import StorageManager
from pathlib import Path

def main():
    # Video details from metadata
    video_id = "uhJJgc-0iTQ"
    year_month = "2025-10"

    # Load metadata
    storage = StorageManager()
    print(f"Loading metadata for video: {video_id} ({year_month})")
    metadata = storage.load_metadata(video_id, year_month)

    if not metadata:
        print(f"Error: Could not load metadata for {video_id}")
        return

    print(f"Title: {metadata['metadata']['title']}")
    print(f"Video path: {metadata['files']['subtitled_video']}")

    # Initialize publisher
    print("\nInitializing publisher...")
    publisher = Publisher(schedule_hours_ahead=0)  # Immediate publish

    # Publish to WeChat
    print("\nPublishing to WeChat Video Channel...")
    result = publisher.publish_to_wechat(
        video_path=metadata['files']['subtitled_video'],
        title=metadata['metadata']['title'],
        tags=metadata['analysis']['topics'][:5],
        category="科技"  # Technology category for AI content
    )

    print(f"\n{'='*60}")
    print(f"Publishing Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Post ID: {result.get('post_id', 'N/A')}")
        print(f"URL: {result.get('url', 'N/A')}")

        # Update metadata
        storage.update_publishing_status(
            video_id,
            year_month,
            'wechat',
            'success',
            post_id=result.get('post_id'),
            url=result.get('url')
        )
        print("\nMetadata updated successfully!")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
