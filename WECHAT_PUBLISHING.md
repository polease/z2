# WeChat Video Channel (视频号) Publishing Guide

This guide explains how to publish videos to WeChat Video Channel using the Z platform.

## Overview

The Z platform integrates with [social-auto-upload](https://github.com/dreammis/social-auto-upload) to automate video publishing to WeChat Video Channel (视频号). This allows you to:

- Automatically publish processed videos with Chinese subtitles
- Set video titles and hashtags
- Choose video categories
- Schedule or immediately publish videos

## Prerequisites

1. **WeChat Account** - You need a WeChat account with Video Channel access
2. **social-auto-upload** - Must be cloned and installed
3. **Playwright** - Browser automation tool for cookie extraction
4. **Chrome/Chromium** - Browser for authentication

## Setup Steps

### 1. Install social-auto-upload

```bash
cd /Users/linzhu/Documents/Project
git clone https://github.com/dreammis/social-auto-upload.git
cd social-auto-upload
pip install -r requirements.txt
playwright install chromium
```

### 2. Extract WeChat Cookies

Run the cookie extraction script:

```bash
cd /Users/linzhu/Documents/Project/z2
python extract_wechat_cookie.py
```

**What happens:**
1. A Chrome browser window opens
2. You'll see the WeChat channels login page
3. Scan the QR code with your WeChat app
4. After login, the browser will pause (Inspector mode)
5. Click "Resume" in the browser inspector
6. Cookies are automatically saved

**Cookie location:**
```
/Users/linzhu/Documents/Project/social-auto-upload/cookies/tencent_uploader/account.json
```

**Note:** You only need to extract cookies once. They will be reused for future uploads.

### 3. Verify Cookie Installation

Check if the cookie file exists:

```bash
ls -l /Users/linzhu/Documents/Project/social-auto-upload/cookies/tencent_uploader/account.json
```

## Usage

### Automatic Publishing (via Pipeline)

When you run the main pipeline, it will automatically publish to WeChat after processing:

```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

The pipeline will:
1. Download and process the video
2. Translate and burn subtitles
3. Generate AI analysis
4. Automatically publish to WeChat Video Channel

### Manual Publishing

To publish an already processed video:

```python
from src.publisher import Publisher
from src.storage import StorageManager

# Load metadata
storage = StorageManager()
metadata = storage.load_metadata("VIDEO_ID", "2025-11")

# Initialize publisher
publisher = Publisher()

# Publish to WeChat
result = publisher.publish_to_wechat(
    video_path=metadata['processing']['subtitled_video_path'],
    title=metadata['title'],
    tags=metadata['analysis']['topics'][:5],
    category="科技"
)

print(f"Status: {result['status']}")
print(f"URL: {result['url']}")
```

### Test Publishing

Use the test script to verify everything works:

```bash
python test_wechat_publish.py
```

This will:
- Check if metadata exists
- Verify video file exists
- Validate cookie authentication
- Prompt for confirmation
- Upload test video to WeChat

## Configuration

### Categories

Available WeChat Video Channel categories:

| Category | Chinese | Use Case |
|----------|---------|----------|
| `知识` | Knowledge | Educational, tutorials, how-to |
| `科技` | Technology | AI, programming, tech news |
| `生活` | Life | Lifestyle, daily vlog |
| `美食` | Food | Cooking, recipes, restaurants |
| `旅行风景` | Travel | Travel vlogs, scenery |
| `音乐` | Music | Music videos, covers |
| `游戏` | Gaming | Gaming content, reviews |

The system automatically determines the best category based on video topics, but you can override it:

```python
publisher.publish_to_wechat(
    video_path=video_path,
    title=title,
    tags=tags,
    category="知识"  # Override category
)
```

### Scheduling

Publish immediately (default):
```python
publisher = Publisher(schedule_hours_ahead=0)
```

Schedule 2 hours ahead:
```python
publisher = Publisher(schedule_hours_ahead=2)
```

Schedule for next day:
```python
publisher = Publisher(schedule_hours_ahead=24)
```

### Tags

WeChat supports hashtags with the `#` symbol. The system automatically:
- Uses the top 5 topics from AI analysis
- Formats them as hashtags
- Adds them to the video description

Example tags:
- `#AI代理`
- `#Python编程`
- `#AI API调用`
- `#工具验证执行`
- `#框架简化`

## Troubleshooting

### Cookie Expired

**Symptom:** Publishing fails with "Cookie authentication failed"

**Solution:**
```bash
python extract_wechat_cookie.py
```
Re-extract cookies by scanning QR code again.

### Browser Not Opening

**Symptom:** extract_wechat_cookie.py doesn't open browser

**Solution:**
1. Check Playwright installation:
   ```bash
   playwright install chromium
   ```
2. Check Chrome path in social-auto-upload config
3. Try running with headed mode (browser visible)

### Upload Fails

**Symptom:** Video upload fails or times out

**Possible causes:**
1. **Large video file** - WeChat has size limits (~1GB)
2. **Network issues** - Check internet connection
3. **Video format issues** - Ensure H.264 codec
4. **Cookie expired** - Re-extract cookies

**Solution:**
- Check video file size: `ls -lh storage/videos/2025-11/*.mp4`
- Verify video codec: `ffprobe video.mp4`
- Re-extract cookies if needed

### Import Errors

**Symptom:** `ImportError: No module named 'uploader'`

**Solution:**
The social-auto-upload path is hardcoded in `src/publisher.py`. Verify:

```python
SOCIAL_AUTO_UPLOAD_PATH = "/Users/linzhu/Documents/Project/social-auto-upload"
```

Update this path if you cloned social-auto-upload to a different location.

### Title/Tags Not Showing

**Symptom:** Video uploads but title/tags are missing

**Possible causes:**
1. Special characters in title
2. Too many tags (limit is usually 5-10)
3. Tag format issues

**Solution:**
- Simplify title (remove emojis, special chars)
- Reduce number of tags
- Ensure tags are strings, not empty

## How It Works

### Architecture

```
Z Platform (src/publisher.py)
    ↓
social-auto-upload (uploader/tencent_uploader/)
    ↓
Playwright (browser automation)
    ↓
WeChat Channels Web Interface
```

### Publishing Flow

1. **Cookie Validation**
   - Check if cookie file exists
   - Validate cookie is not expired
   - If invalid, return error

2. **Video Upload**
   - Open WeChat Channels in browser
   - Navigate to upload page
   - Select video file
   - Wait for upload to complete

3. **Metadata Setting**
   - Fill in title
   - Add hashtags
   - Select category
   - Set as original (if configured)

4. **Publishing**
   - Schedule time (if configured)
   - Click publish button
   - Wait for confirmation
   - Save updated cookies

5. **Verification**
   - Check for success message
   - Return status and URL

## Best Practices

### 1. Cookie Management
- Re-extract cookies monthly or when they expire
- Keep cookies secure (don't commit to Git)
- One cookie per WeChat account

### 2. Video Quality
- Use H.264 codec for best compatibility
- Keep file size under 500MB for faster upload
- Use 1920x1080 or 1280x720 resolution
- Include burned Chinese subtitles

### 3. Title and Tags
- Keep titles under 30 characters
- Use relevant hashtags (3-5 recommended)
- Avoid special characters that may break rendering
- Choose appropriate category for better discovery

### 4. Publishing Strategy
- Schedule videos for peak viewing times
- Don't publish too frequently (WeChat may throttle)
- Monitor upload success rate
- Re-publish manually if automated upload fails

## Advanced Usage

### Custom Publisher Configuration

```python
from src.publisher import Publisher

publisher = Publisher(
    storage_path="./storage",
    cookie_base_path="/custom/path/to/cookies",
    schedule_hours_ahead=2
)
```

### Batch Publishing

```python
from pathlib import Path
from src.publisher import Publisher
from src.storage import StorageManager

storage = StorageManager()
publisher = Publisher()

# Get all processed videos from 2025-11
video_dir = Path("storage/videos/2025-11")
for video_file in video_dir.glob("*_zh_subbed.mp4"):
    video_id = video_file.stem.replace("_zh_subbed", "")

    # Load metadata
    metadata = storage.load_metadata(video_id, "2025-11")

    # Publish
    result = publisher.publish_to_wechat(
        video_path=str(video_file),
        title=metadata['title'],
        tags=metadata['analysis']['topics'][:5],
        category="科技"
    )

    print(f"{video_id}: {result['status']}")
```

### Integration with Other Platforms

The `Publisher` class also supports Bilibili (placeholder):

```python
# Publish to both platforms
results = publisher.publish(
    video_path=video_path,
    metadata=metadata,
    analysis=analysis
)

print(f"WeChat: {results['wechat']['status']}")
print(f"Bilibili: {results['bilibili']['status']}")
```

## References

- [social-auto-upload GitHub](https://github.com/dreammis/social-auto-upload)
- [WeChat Channels Official](https://channels.weixin.qq.com)
- [Playwright Documentation](https://playwright.dev/python/)

## Support

If you encounter issues:

1. Check this guide first
2. Review logs in `logs/z2.log`
3. Test with `python test_wechat_publish.py`
4. Check social-auto-upload documentation
5. Verify cookie is valid and not expired

For bugs or feature requests, open an issue in the Z platform repository.
