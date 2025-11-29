"""
Translation and Chinese SRT generation module
"""

import os
import re
from openai import OpenAI
from typing import Dict, List
from .utils.logger import get_app_logger
from .utils.srt_utils import create_srt_file, read_srt_file, split_long_subtitle

logger = get_app_logger()


class Translator:
    """Translate English subtitles to Chinese and generate SRT files"""

    def __init__(
        self,
        api_key: str,
        storage_path: str = "./storage",
        model: str = "gpt-4o-mini",
        max_chars_per_line: int = 42
    ):
        """
        Initialize translator

        Args:
            api_key: OpenAI API key
            storage_path: Base storage path
            model: OpenAI model to use
            max_chars_per_line: Maximum characters per subtitle line
        """
        self.client = OpenAI(api_key=api_key)
        self.storage_path = storage_path
        self.subtitle_path = os.path.join(storage_path, "subtitles")
        self.model = model
        self.max_chars_per_line = max_chars_per_line

        # Ensure subtitle directory exists
        os.makedirs(self.subtitle_path, exist_ok=True)

    def translate(
        self,
        english_transcript: Dict,
        video_id: str,
        year_month: str
    ) -> Dict:
        """
        Translate English transcript to Chinese and generate SRT file

        Args:
            english_transcript: English transcript data from transcriber
            video_id: Video ID
            year_month: Year-month for directory organization (e.g., "2024-01")

        Returns:
            Dictionary with Chinese transcript and SRT file path
        """
        logger.info(f"Translating transcript for video: {video_id}")

        segments = english_transcript['segments']

        # Translate segments in batches
        chinese_segments = self._translate_segments(segments)

        # Create Chinese SRT file
        subtitle_dir = os.path.join(self.subtitle_path, year_month)
        os.makedirs(subtitle_dir, exist_ok=True)

        chinese_srt_path = os.path.join(subtitle_dir, f"{video_id}_zh.srt")
        create_srt_file(chinese_segments, chinese_srt_path)

        logger.info(f"Created Chinese SRT file: {chinese_srt_path}")

        # Read back to get properly formatted segments
        formatted_segments = read_srt_file(chinese_srt_path)

        # Combine full text
        full_text = "\n".join([seg['text'] for seg in formatted_segments])

        result = {
            'language': 'zh-CN',
            'srt_file_path': chinese_srt_path,
            'segments': formatted_segments,
            'full_text': full_text,
            'segment_count': len(formatted_segments)
        }

        logger.info(f"Successfully translated {len(formatted_segments)} segments to Chinese")
        return result

    def _translate_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Translate subtitle segments to Chinese

        Args:
            segments: List of English subtitle segments

        Returns:
            List of Chinese subtitle segments
        """
        chinese_segments = []
        batch_size = 100  # Process 100 segments at a time

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            logger.info(f"Translating batch {i//batch_size + 1} ({len(batch)} segments)")

            translations = self._translate_batch(batch)

            # Combine with timing information
            for seg, translation in zip(batch, translations):
                # Check if translation is too long
                if len(translation) > self.max_chars_per_line:
                    # For now, just use the translation as-is
                    # TODO: Could implement splitting into multiple subtitle frames
                    pass

                chinese_segments.append({
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': translation
                })

        return chinese_segments

    def _translate_batch(self, segments: List[Dict]) -> List[str]:
        """
        Translate a batch of segments using OpenAI

        Args:
            segments: List of English segments

        Returns:
            List of Chinese translations
        """
        # Prepare segments text with numbering
        segments_text = "\n".join([
            f"{i+1}. {seg['text']}"
            for i, seg in enumerate(segments)
        ])

        segment_count = len(segments)
        prompt = f"""Translate the following {segment_count} English subtitle segments to Chinese (Simplified).

CRITICAL RULES:
1. Output EXACTLY {segment_count} translations - no more, no less
2. Each translation must be on a SINGLE line (no line breaks within a translation)
3. Number each line exactly as: "1. translation", "2. translation", etc.
4. One-to-one mapping: segment 1 → translation 1, segment 2 → translation 2, etc.
5. Do NOT split, merge, or skip any segments
6. Do NOT add explanations or notes

Translation guidelines:
- Use appropriate AI/tech terminology in Chinese
- Keep translations concise for subtitles

English Segments ({segment_count} total):
{segments_text}

Output EXACTLY {segment_count} numbered Chinese translations:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            translations_text = response.choices[0].message.content.strip()

            # Initialize translations array with placeholders
            segment_count = len(segments)
            translations = ["[翻译缺失]"] * segment_count

            # Parse numbered translations and place them by index
            parsed_count = 0
            for line in translations_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Match number prefix pattern: "1. ", "12. ", "100. " etc.
                match = re.match(r'^(\d+)\.\s*(.+)$', line)
                if match:
                    num = int(match.group(1))
                    text = match.group(2)
                    # Place translation at correct index (1-based to 0-based)
                    if 1 <= num <= segment_count:
                        translations[num - 1] = text
                        parsed_count += 1
                    else:
                        logger.warning(f"Translation number {num} out of range (1-{segment_count})")

            # Log if there were missing translations
            if parsed_count != segment_count:
                missing_indices = [i + 1 for i, t in enumerate(translations) if t == "[翻译缺失]"]
                logger.warning(
                    f"Translation count mismatch: expected {segment_count}, got {parsed_count}. "
                    f"Missing indices: {missing_indices[:20]}{'...' if len(missing_indices) > 20 else ''}"
                )

            return translations

        except Exception as e:
            logger.error(f"Failed to translate batch: {str(e)}")
            # Return fallback translations
            return ["[翻译失败]" for _ in segments]

    def translate_text(self, text: str) -> str:
        """
        Translate a single text string to Chinese

        Args:
            text: English text

        Returns:
            Chinese translation
        """
        prompt = f"""Translate the following English text to Chinese (Simplified):

{text}

Output only the Chinese translation:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            translation = response.choices[0].message.content.strip()
            return translation

        except Exception as e:
            logger.error(f"Failed to translate text: {str(e)}")
            return "[翻译失败]"
