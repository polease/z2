"""
Publishing module for WeChat and Bilibili using social-auto-upload integration
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
from .utils.logger import get_app_logger

# Add social-auto-upload to Python path
SOCIAL_AUTO_UPLOAD_PATH = "/Users/linzhu/Documents/Project/social-auto-upload"
if SOCIAL_AUTO_UPLOAD_PATH not in sys.path:
    sys.path.insert(0, SOCIAL_AUTO_UPLOAD_PATH)

logger = get_app_logger()


class Publisher:
    """Publish videos to WeChat and Bilibili using social-auto-upload"""

    def __init__(
        self,
        storage_path: str = "./storage",
        cookie_base_path: str = None,
        schedule_hours_ahead: int = 0
    ):
        """
        Initialize publisher

        Args:
            storage_path: Base storage path
            cookie_base_path: Base path for cookie files (defaults to social-auto-upload cookies folder)
            schedule_hours_ahead: Hours ahead to schedule (0 = immediate publish)
        """
        self.storage_path = storage_path
        self.cookie_base_path = cookie_base_path or os.path.join(SOCIAL_AUTO_UPLOAD_PATH, "cookies")
        self.schedule_hours_ahead = schedule_hours_ahead

        # Ensure cookie directories exist
        os.makedirs(os.path.join(self.cookie_base_path, "tencent_uploader"), exist_ok=True)

    def publish_to_wechat(
        self,
        video_path: str,
        title: str,
        tags: list,
        category: str = "知识"
    ) -> Dict:
        """
        Publish video to WeChat Video Channel (视频号) using social-auto-upload

        Args:
            video_path: Path to video file with burned subtitles
            title: Video title
            tags: List of hashtags (without # symbol)
            category: Video category (知识, 科技, etc.)

        Returns:
            Dictionary with publishing result
        """
        logger.info("Publishing to WeChat Video Channel...")

        try:
            # Import WeChat uploader modules
            from uploader.tencent_uploader.main import weixin_setup, TencentVideo
            from utils.constant import TencentZoneTypes

            # Cookie file path
            account_file = Path(self.cookie_base_path) / "tencent_uploader" / "account.json"

            # Check and setup cookie
            cookie_valid = asyncio.run(weixin_setup(str(account_file), handle=False))

            if not cookie_valid:
                logger.error("WeChat cookie is invalid or missing. Please run cookie extraction first.")
                return {
                    'status': 'failed',
                    'platform': 'wechat',
                    'message': 'Cookie authentication failed. Please extract cookies first.',
                    'post_id': None,
                    'url': None
                }

            # Determine publish time
            if self.schedule_hours_ahead > 0:
                publish_date = datetime.now() + timedelta(hours=self.schedule_hours_ahead)
            else:
                publish_date = 0  # Immediate publish

            # Map category to TencentZoneTypes
            category_value = self._map_wechat_category(category)

            # Create TencentVideo instance and upload
            logger.info(f"Uploading to WeChat: {title}")
            logger.info(f"Tags: {tags}")
            logger.info(f"Category: {category}")

            uploader = TencentVideo(
                title=title,
                file_path=video_path,
                tags=tags,
                publish_date=publish_date,
                account_file=str(account_file),
                category=category_value
            )

            # Run upload
            asyncio.run(uploader.main())

            logger.info("Successfully published to WeChat Video Channel")

            return {
                'status': 'success',
                'platform': 'wechat',
                'message': 'Video published successfully',
                'post_id': None,  # WeChat doesn't return post ID immediately
                'url': 'https://channels.weixin.qq.com/platform/post/list'
            }

        except ImportError as e:
            logger.error(f"Failed to import social-auto-upload modules: {str(e)}")
            return {
                'status': 'failed',
                'platform': 'wechat',
                'message': f'Import error: {str(e)}',
                'post_id': None,
                'url': None
            }

        except Exception as e:
            logger.error(f"Failed to publish to WeChat: {str(e)}")
            return {
                'status': 'failed',
                'platform': 'wechat',
                'message': str(e),
                'post_id': None,
                'url': None
            }

    def _map_wechat_category(self, category: str) -> str:
        """Map generic category to WeChat category"""
        category_map = {
            '知识': '知识',
            '科技': '科技',
            '技术': '科技',
            'AI': '科技',
            '人工智能': '科技',
            '编程': '知识',
            '教程': '知识',
            '生活': '生活',
            '美食': '美食',
            '旅行': '旅行风景',
            '音乐': '音乐',
            '游戏': '游戏'
        }
        return category_map.get(category, '知识')

    def publish_to_bilibili(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        cover_url: str,
        category: str = "科技"
    ) -> Dict:
        """
        Publish video to Bilibili

        Args:
            video_path: Path to video file with burned subtitles
            title: Video title
            description: Video description
            tags: List of tags
            cover_url: Cover image URL
            category: Video category

        Returns:
            Dictionary with publishing result
        """
        logger.info("Publishing to Bilibili...")
        logger.warning("Bilibili publishing not yet implemented - placeholder only")

        # TODO: Implement Bilibili Upload API integration
        # Steps:
        # 1. Authenticate with Bilibili API
        # 2. Upload video file (may require chunked upload)
        # 3. Submit video metadata
        # 4. Set tags and category
        # 5. Publish video
        # 6. Get published URL and video ID

        # Placeholder response
        return {
            'status': 'not_implemented',
            'platform': 'bilibili',
            'message': 'Bilibili API integration pending',
            'video_id': None,
            'url': None
        }

    def publish(
        self,
        video_path: str,
        metadata: Dict,
        analysis: Dict
    ) -> Dict:
        """
        Publish to all enabled platforms

        Args:
            video_path: Path to video file with burned subtitles
            metadata: Video metadata
            analysis: Content analysis data

        Returns:
            Dictionary with results for each platform
        """
        logger.info("Starting multi-platform publishing...")

        # Prepare title and tags
        title = metadata.get('title') or metadata.get('metadata', {}).get('title', 'Untitled')
        tags = analysis.get('topics', [])[:5]  # Limit to 5 tags for WeChat
        category = self._determine_category(analysis.get('topics', []))

        results = {}

        # Publish to WeChat
        try:
            wechat_result = self.publish_to_wechat(
                video_path,
                title,
                tags,
                category
            )

            results['wechat'] = wechat_result

        except Exception as e:
            logger.error(f"Failed to publish to WeChat: {str(e)}")
            results['wechat'] = {'status': 'failed', 'error': str(e)}

        # Publish to Bilibili
        try:
            bilibili_description = self._generate_bilibili_description(
                analysis['summary'],
                analysis['key_insights'],
                metadata['youtube_url']
            )

            bilibili_tags = analysis.get('topics', [])[:10]  # Max 10 tags

            bilibili_result = self.publish_to_bilibili(
                video_path,
                title,
                bilibili_description,
                bilibili_tags,
                metadata.get('thumbnail_url', '')
            )

            results['bilibili'] = bilibili_result

        except Exception as e:
            logger.error(f"Failed to publish to Bilibili: {str(e)}")
            results['bilibili'] = {'status': 'failed', 'error': str(e)}

        logger.info("Multi-platform publishing completed")
        return results

    def _determine_category(self, topics: list) -> str:
        """Determine video category based on topics"""
        # Map topics to categories
        topic_str = " ".join(topics).lower()

        if any(keyword in topic_str for keyword in ['ai', '人工智能', 'agent', '机器学习']):
            return '科技'
        elif any(keyword in topic_str for keyword in ['编程', 'python', 'code', '代码']):
            return '知识'
        elif any(keyword in topic_str for keyword in ['美食', 'food', '烹饪']):
            return '美食'
        elif any(keyword in topic_str for keyword in ['旅行', 'travel', '风景']):
            return '旅行风景'
        else:
            return '知识'  # Default category

    def _generate_bilibili_description(
        self,
        summary: str,
        key_insights: list,
        youtube_url: str
    ) -> str:
        """Generate Bilibili video description"""
        insights_text = "\n".join([f"• {insight}" for insight in key_insights])

        return f"""{summary}

📌 关键洞察：
{insights_text}

🔗 原视频：{youtube_url}

#AI #人工智能 #技术"""
