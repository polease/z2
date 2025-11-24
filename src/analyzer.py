"""
Content analysis and summary generation module
"""

from openai import OpenAI
from typing import Dict, List
from .utils.logger import get_app_logger

logger = get_app_logger()


class ContentAnalyzer:
    """Generate summaries and insights from video content"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize content analyzer

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze(
        self,
        chinese_transcript: Dict,
        video_metadata: Dict
    ) -> Dict:
        """
        Analyze video content and generate summary and insights

        Args:
            chinese_transcript: Chinese transcript data
            video_metadata: Video metadata

        Returns:
            Dictionary with summary, insights, highlights, and topics
        """
        logger.info(f"Analyzing content for video: {video_metadata['video_id']}")

        title = video_metadata.get('title', 'Unknown')
        channel = video_metadata.get('channel', 'Unknown')
        full_text = chinese_transcript['full_text']

        # Generate analysis
        analysis = self._generate_analysis(full_text, title, channel)

        logger.info("Content analysis completed")
        logger.info(f"Generated {len(analysis['key_insights'])} key insights")
        logger.info(f"Identified {len(analysis['highlights'])} highlights")
        logger.info(f"Extracted {len(analysis['topics'])} topics")

        return analysis

    def _generate_analysis(
        self,
        transcript: str,
        title: str,
        channel: str
    ) -> Dict:
        """
        Generate comprehensive content analysis

        Args:
            transcript: Chinese transcript text
            title: Video title
            channel: Channel name

        Returns:
            Analysis dictionary
        """
        prompt = f"""You are an AI content analyst. Analyze the following video transcript and generate:

1. A concise summary (2-3 paragraphs in Chinese)
2. Key insights (3-5 bullet points in Chinese)
3. Important highlights with approximate timestamps (if identifiable from content flow)
4. Main topics covered (3-7 topic keywords in Chinese)

Video Title: {title}
Channel: {channel}

Transcript (Chinese):
{transcript[:8000]}  # Limit to avoid token limits

Please output in the following JSON format:
{{
  "summary": "视频摘要...",
  "key_insights": [
    "关键洞察1",
    "关键洞察2",
    "关键洞察3"
  ],
  "highlights": [
    {{
      "description": "重要内容描述"
    }}
  ],
  "topics": ["话题1", "话题2", "话题3"]
}}

Output only valid JSON:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI content analyst. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            import json
            analysis_text = response.choices[0].message.content.strip()
            analysis = json.loads(analysis_text)

            # Validate structure
            if 'summary' not in analysis:
                analysis['summary'] = "暂无摘要"
            if 'key_insights' not in analysis:
                analysis['key_insights'] = []
            if 'highlights' not in analysis:
                analysis['highlights'] = []
            if 'topics' not in analysis:
                analysis['topics'] = []

            return analysis

        except Exception as e:
            logger.error(f"Failed to generate analysis: {str(e)}")

            # Return fallback analysis
            return {
                'summary': f"这是一个关于{title}的视频。",
                'key_insights': ["内容分析失败"],
                'highlights': [],
                'topics': ["AI", "技术"]
            }

    def generate_description(
        self,
        summary: str,
        key_insights: List[str],
        youtube_url: str,
        platform: str = "bilibili"
    ) -> str:
        """
        Generate platform-specific description

        Args:
            summary: Content summary
            key_insights: List of key insights
            youtube_url: Original YouTube URL
            platform: Target platform (bilibili or wechat)

        Returns:
            Formatted description text
        """
        if platform == "bilibili":
            insights_text = "\n".join([f"• {insight}" for insight in key_insights])
            description = f"""{summary}

📌 关键洞察：
{insights_text}

🔗 原视频：{youtube_url}

#AI #人工智能 #技术"""

        elif platform == "wechat":
            description = f"""{summary}

原视频：{youtube_url}"""

        else:
            description = summary

        return description

    def generate_tags(self, topics: List[str], max_tags: int = 10) -> List[str]:
        """
        Generate tags from topics

        Args:
            topics: List of topic keywords
            max_tags: Maximum number of tags

        Returns:
            List of tags
        """
        # Basic tag generation - can be enhanced
        base_tags = ["AI", "人工智能", "技术", "科技"]

        tags = base_tags + topics
        tags = list(set(tags))  # Remove duplicates

        return tags[:max_tags]
