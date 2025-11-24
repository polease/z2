# Quick Start Guide - WeChat Publishing

## 🚀 Three Steps to Start Publishing

### 1️⃣ Extract WeChat Cookies (One-time setup)

```bash
cd /Users/linzhu/Documents/Project/z2
source venv/bin/activate
python extract_wechat_cookie.py
```

**What you'll do:**
- Browser opens → Scan QR code with WeChat
- Browser pauses → Click "Resume" button
- Done! Cookies saved automatically

⏱️ **Takes:** 1-2 minutes

---

### 2️⃣ Test Publishing (Optional but recommended)

```bash
python test_wechat_publish.py
```

**What it does:**
- Tests with already-processed video
- Verifies cookies work
- Uploads to your WeChat channel

⏱️ **Takes:** 2-3 minutes

---

### 3️⃣ Process & Publish New Video

```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Full pipeline:**
1. ✅ Downloads video
2. ✅ Extracts/transcribes subtitles
3. ✅ Translates to Chinese
4. ✅ Burns subtitles into video
5. ✅ Generates AI summary
6. ✅ **Publishes to WeChat automatically**

⏱️ **Takes:** 7-15 minutes per video

---

## 📝 Example Workflow

```bash
# Activate environment
source venv/bin/activate

# Extract cookies (first time only)
python extract_wechat_cookie.py

# Process a video
python -m src.main "https://www.youtube.com/watch?v=uR_lvAZFBw0"

# Check the output
ls -lh storage/videos/2025-11/
# You'll see: VIDEO_ID_zh_subbed.mp4

# Check metadata
cat storage/data/2025-11/VIDEO_ID.json
```

---

## ⚙️ Common Customizations

### Schedule Publishing

```python
from src.publisher import Publisher

# Schedule 2 hours ahead
publisher = Publisher(schedule_hours_ahead=2)
```

### Change Category

```python
# Override auto-detection
result = publisher.publish_to_wechat(
    video_path=path,
    title=title,
    tags=tags,
    category="科技"  # or "知识", "美食", etc.
)
```

### Manual Publishing

```python
from src.publisher import Publisher
from src.storage import StorageManager

storage = StorageManager()
metadata = storage.load_metadata("VIDEO_ID", "2025-11")
publisher = Publisher()

result = publisher.publish_to_wechat(
    video_path=metadata['processing']['subtitled_video_path'],
    title=metadata['title'],
    tags=metadata['analysis']['topics'][:5],
    category="科技"
)
```

---

## 🔍 Check Status

### View Logs

```bash
tail -f logs/z2.log
```

### Check Published Videos

After publishing, visit:
- https://channels.weixin.qq.com/platform/post/list

### Verify Cookie

```bash
ls -l /Users/linzhu/Documents/Project/social-auto-upload/cookies/tencent_uploader/account.json
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Cookie extraction fails | Run `playwright install chromium` |
| "Cookie authentication failed" | Re-run `python extract_wechat_cookie.py` |
| Import errors | Check social-auto-upload path in `src/publisher.py` |
| Upload fails | Check video file size (< 500MB recommended) |

---

## 📚 Full Documentation

For detailed information:
- **SETUP_COMPLETE.md** - What's been done
- **WECHAT_PUBLISHING.md** - Complete publishing guide
- **README.md** - Full project documentation

---

## ✨ Tips

1. **Cookie Lifespan:** Cookies typically last 1-2 months. Re-extract when they expire.

2. **Best Practices:**
   - Keep videos under 500MB for faster uploads
   - Use descriptive titles (< 30 characters)
   - Add 3-5 relevant hashtags
   - Don't publish too frequently (WeChat may throttle)

3. **Monitoring:**
   - Check `logs/z2.log` for detailed execution logs
   - Publishing status is saved in metadata JSON files

4. **Batch Processing:**
   - Process multiple videos sequentially
   - The cookie will be reused automatically
   - Monitor for rate limiting

---

**You're all set! Start with extracting cookies and you'll be publishing in minutes.** 🎉
