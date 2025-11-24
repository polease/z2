#!/usr/bin/env python3
"""
WeChat Cookie Extraction Script
This script helps extract WeChat Video Channel (视频号) authentication cookies
"""

import sys
import asyncio
from pathlib import Path

# Add social-auto-upload to path
SOCIAL_AUTO_UPLOAD_PATH = "/Users/linzhu/Documents/Project/social-auto-upload"
sys.path.insert(0, SOCIAL_AUTO_UPLOAD_PATH)

from uploader.tencent_uploader.main import weixin_setup


async def extract_cookie():
    """Extract WeChat cookie through browser login"""
    # Cookie file path
    cookie_dir = Path(SOCIAL_AUTO_UPLOAD_PATH) / "cookies" / "tencent_uploader"
    cookie_dir.mkdir(parents=True, exist_ok=True)
    account_file = cookie_dir / "account.json"

    print("=" * 80)
    print("WeChat Video Channel (视频号) Cookie Extraction")
    print("=" * 80)
    print()
    print("This script will open a browser window for you to login to WeChat.")
    print()
    print("STEPS:")
    print("1. A browser window will open")
    print("2. Scan the QR code with your WeChat app")
    print("3. After successful login, the browser will pause")
    print("4. Click the 'Resume' button in the browser inspector to continue")
    print("5. The cookie will be automatically saved")
    print()
    print(f"Cookie will be saved to: {account_file}")
    print()
    input("Press Enter to continue...")

    # Run cookie extraction
    success = await weixin_setup(str(account_file), handle=True)

    if success:
        print()
        print("✓ Cookie extracted successfully!")
        print(f"Cookie saved to: {account_file}")
        print()
        print("You can now use the Z platform to publish videos to WeChat.")
    else:
        print()
        print("✗ Failed to extract cookie")
        print("Please try again or check your WeChat login status.")

    return success


if __name__ == '__main__':
    asyncio.run(extract_cookie())
