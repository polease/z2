#!/usr/bin/env python3
"""
Test script for WeChat publishing
Tests the integration with social-auto-upload for WeChat Video Channel
"""

import sys
from pathlib import Path
from src.publisher import Publisher
from src.storage import StorageManager


def test_wechat_publish():
    """Test WeChat publishing with an already processed video"""
    print("=" * 80)
    print("WeChat Publishing Test")
    print("=" * 80)
    print()

    # Check if we have a processed video
    storage = StorageManager()
    video_id = "uR_lvAZFBw0"
    year_month = "2025-11"

    print(f"Loading metadata for video: {video_id}")
    print(f"Year-month: {year_month}")
    print()

    try:
        metadata = storage.load_metadata(video_id, year_month)
        print("✓ Metadata loaded successfully")
        print(f"  Title: {metadata['metadata']['title']}")
        print(f"  Topics: {metadata['analysis']['topics']}")
        print()

        # Check if video file exists
        video_path = metadata['files']['subtitled_video']
        if not Path(video_path).exists():
            print(f"✗ Video file not found: {video_path}")
            return

        print(f"✓ Video file exists: {video_path}")
        print()

        # Initialize publisher
        print("Initializing publisher...")
        publisher = Publisher()
        print()

        # Check cookie status
        print("Checking WeChat cookie authentication...")
        cookie_path = Path("/Users/linzhu/Documents/Project/social-auto-upload/cookies/tencent_uploader/account.json")

        if not cookie_path.exists():
            print(f"✗ Cookie file not found: {cookie_path}")
            print()
            print("Please run: python extract_wechat_cookie.py")
            return

        print(f"✓ Cookie file exists: {cookie_path}")
        print()

        # Attempt to publish
        print("Publishing to WeChat Video Channel...")
        print("This will:")
        print("1. Validate cookie authentication")
        print("2. Upload video to WeChat")
        print("3. Set title and tags")
        print("4. Publish immediately")
        print()

        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return

        result = publisher.publish_to_wechat(
            video_path=video_path,
            title=metadata['metadata']['title'],
            tags=metadata['analysis']['topics'][:5],
            category="科技"
        )

        print()
        print("=" * 80)
        print("Publishing Result")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Platform: {result['platform']}")
        print(f"Message: {result['message']}")
        if result['url']:
            print(f"URL: {result['url']}")
        print()

        if result['status'] == 'success':
            print("✓ Successfully published to WeChat Video Channel!")
            print(f"  Check your videos at: {result['url']}")
        else:
            print("✗ Publishing failed")
            print(f"  Error: {result['message']}")

    except FileNotFoundError as e:
        print(f"✗ Metadata not found: {e}")
        print()
        print("Please run the pipeline first:")
        print(f'  python -m src.main "https://www.youtube.com/watch?v={video_id}"')

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_wechat_publish()
