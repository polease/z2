# Z — AI Knowledge Distillery Platform

> Delivering the world's most important AI knowledge to China — accurately, quickly, and insightfully.

## Overview

Z is an AI-powered content processing platform that:
- Downloads YouTube AI content videos
- Extracts or transcribes subtitles
- Translates to high-quality Chinese
- Burns subtitles into videos
- Generates AI-powered summaries and insights
- Publishes to Chinese platforms (WeChat, Bilibili)

## Features (MVP)

✅ **YouTube Video Processing**
- Download videos with metadata
- Extract existing subtitles or transcribe with Whisper
- Automatic subtitle detection

✅ **Translation & Subtitles**
- High-quality translation using OpenAI GPT-4
- SRT format subtitle generation
- Timestamp-aligned Chinese subtitles

✅ **Video Processing**
- Burn Chinese subtitles into videos using FFmpeg
- Customizable subtitle styling
- High-quality video output

✅ **Content Analysis**
- AI-generated summaries
- Key insights extraction
- Topic identification
- Highlight detection

✅ **Storage & Metadata**
- JSON-based metadata storage
- Organized file structure
- Complete processing history

✅ **Publishing**
- WeChat Video Channel (视频号) integration using social-auto-upload
- Bilibili upload integration (pending)

## Project Structure

```
z2/
├── src/                      # Source code
│   ├── main.py              # Main pipeline orchestrator
│   ├── downloader.py        # YouTube video downloader
│   ├── transcriber.py       # Subtitle/transcription processor
│   ├── translator.py        # Translation & SRT generation
│   ├── video_processor.py  # Video processing & subtitle burning
│   ├── analyzer.py          # Content analysis
│   ├── storage.py           # Storage management
│   ├── publisher.py         # Publishing (placeholder)
│   └── utils/               # Utility modules
│       ├── config.py        # Configuration management
│       ├── logger.py        # Logging utilities
│       └── srt_utils.py     # SRT file utilities
├── storage/                 # Data storage
│   ├── videos/              # Downloaded & processed videos
│   ├── subtitles/           # SRT files
│   └── data/                # JSON metadata
├── config/                  # Configuration
│   └── config.yaml          # Main configuration
├── documents/               # Documentation
│   └── backlog/             # Project backlog & design docs
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- FFmpeg (with libass for subtitle support)
- OpenAI API key

### Step 1: Install System Dependencies

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg libass-dev
```

**Windows:**
Download FFmpeg from https://ffmpeg.org/download.html

### Step 2: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for WeChat publishing)
playwright install chromium
```

### Step 3: Clone and Setup social-auto-upload

WeChat publishing requires the social-auto-upload tool:

```bash
# Clone to parent directory
cd /Users/linzhu/Documents/Project
git clone https://github.com/dreammis/social-auto-upload.git
cd social-auto-upload

# Copy configuration file
cp conf.example.py conf.py

# No need to install dependencies - they're already in z2's requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# Required:
OPENAI_API_KEY=sk-your-api-key-here
```

### Step 5: Extract WeChat Cookies

Before publishing to WeChat, you need to extract authentication cookies:

```bash
# Run the cookie extraction script
python extract_wechat_cookie.py
```

This will:
1. Open a browser window
2. Show a QR code to scan with WeChat
3. Wait for you to login
4. Save authentication cookies automatically

The cookie will be saved to: `/Users/linzhu/Documents/Project/social-auto-upload/cookies/tencent_uploader/account.json`

**Note:** You only need to do this once. The cookie will be reused for future uploads.

### Step 6: Create Storage Directories

```bash
mkdir -p storage/{videos,subtitles,data}
mkdir -p logs
```

## Usage

### Basic Usage

Process a YouTube video:

```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

### With Custom Config

```bash
python -m src.main "https://www.youtube.com/watch?v=VIDEO_ID" --config config/config.yaml
```

### Pipeline Stages

The pipeline processes videos through 7 stages:

1. **Download Video** - Downloads video and extracts metadata
2. **Process Subtitles** - Extracts YouTube subtitles or transcribes with Whisper
3. **Translate** - Translates English to Chinese, generates SRT file
4. **Burn Subtitles** - Burns Chinese subtitles into video using FFmpeg
5. **Analyze Content** - Generates summary, insights, and topics
6. **Save Metadata** - Stores all data in JSON format
7. **Publish** - Uploads to WeChat and Bilibili (placeholder)

### Output

For each processed video, the system creates:

```
storage/
├── videos/2024-01/
│   ├── VIDEO_ID.mp4                 # Original video
│   └── VIDEO_ID_zh_subbed.mp4       # Video with Chinese subtitles
├── subtitles/2024-01/
│   ├── VIDEO_ID_en.srt              # English subtitles
│   └── VIDEO_ID_zh.srt              # Chinese subtitles
└── data/2024-01/
    └── VIDEO_ID.json                # Complete metadata
```

## Publishing to WeChat

Once you've extracted cookies, the pipeline will automatically publish to WeChat Video Channel after processing.

### Manual Publishing

To publish an already processed video:

```python
from src.publisher import Publisher
from src.storage import StorageManager
from pathlib import Path

# Load metadata
storage = StorageManager()
metadata = storage.load_metadata("uR_lvAZFBw0", "2025-11")

# Initialize publisher
publisher = Publisher()

# Publish to WeChat
result = publisher.publish_to_wechat(
    video_path=metadata['processing']['subtitled_video_path'],
    title=metadata['title'],
    tags=metadata['analysis']['topics'][:5],
    category="科技"
)

print(f"Published: {result['status']}")
```

### WeChat Categories

Available categories for WeChat Video Channel:
- `知识` (Knowledge) - Default for educational content
- `科技` (Technology) - AI, programming, tech
- `生活` (Life) - Lifestyle content
- `美食` (Food) - Cooking, recipes
- `旅行风景` (Travel) - Travel and scenery
- `音乐` (Music) - Music content
- `游戏` (Gaming) - Gaming content

The system automatically determines the best category based on video topics.

### Publishing Settings

You can configure publishing behavior in your code:

```python
# Immediate publish
publisher = Publisher(schedule_hours_ahead=0)

# Schedule 2 hours ahead
publisher = Publisher(schedule_hours_ahead=2)

# Custom cookie path
publisher = Publisher(cookie_base_path="/path/to/cookies")
```

## Configuration

Edit `config/config.yaml` to customize:

- **Storage paths** - Where files are saved
- **Whisper settings** - Model size, device (CPU/GPU)
- **OpenAI settings** - Model, temperature, token limits
- **Translation settings** - Chunk size, subtitle character limits
- **Subtitle styling** - Font, size, colors
- **Publishing settings** - Platform-specific options

## Processing Time

For a typical 10-minute video:

- Download: ~30 seconds
- Subtitle extraction: ~5 seconds
- Whisper transcription (if needed): ~2-5 minutes (CPU) or ~30-60 seconds (GPU)
- Translation: ~30-60 seconds
- Subtitle burning: ~1-3 minutes
- Analysis: ~30 seconds
- Publishing: ~2-3 minutes per platform

**Total: ~7-15 minutes** (depending on whether transcription is needed)

## Troubleshooting

### FFmpeg Errors

If subtitle burning fails:
```bash
# Verify FFmpeg installation
ffmpeg -version

# Check libass support
ffmpeg -filters | grep subtitles
```

### Font Issues

If Chinese characters don't display:
- Install SimHei or Microsoft YaHei font on your system
- Update `subtitle_style.font_name` in config.yaml

### Whisper Performance

For faster transcription:
- Use smaller Whisper model (`tiny`, `base`, `small`)
- Enable GPU: set `WHISPER_DEVICE=cuda` in .env
- Install CUDA toolkit for GPU support

### OpenAI API Errors

- Check API key is valid
- Verify sufficient API credits
- Reduce chunk sizes if hitting token limits

## Development Status

### Completed (MVP)
- [x] Video download and metadata extraction
- [x] Subtitle extraction/transcription
- [x] Translation to Chinese
- [x] SRT file generation
- [x] Subtitle burning into video
- [x] Content analysis and insights
- [x] Storage management
- [x] Pipeline orchestration

### In Progress
- [x] WeChat Video Channel (视频号) integration ✓

### Pending
- [ ] Bilibili Upload API integration
- [ ] Automated channel monitoring
- [ ] Video editing and highlights
- [ ] Knowledge graph
- [ ] Web dashboard

## License

Copyright © 2024 Z Platform

## Support

For issues and questions:
- Check the documentation in `documents/backlog/`
- Review the design document: `documents/backlog/20251123-AIKnowledgeDistilleryPlatform/02. Design.md`
