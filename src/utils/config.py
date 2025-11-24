"""
Configuration management for Z platform
"""

import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any


class Config:
    """Configuration manager for Z platform"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration manager

        Args:
            config_path: Path to YAML configuration file
        """
        # Load environment variables
        load_dotenv()

        # Load YAML configuration
        self.config_path = config_path
        self.config_data = self._load_yaml_config()

    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key

        Args:
            key: Configuration key in dot notation (e.g., "storage.base_path")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key from environment"""
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return key

    @property
    def wechat_app_id(self) -> str:
        """Get WeChat App ID from environment"""
        return os.getenv('WECHAT_APP_ID', '')

    @property
    def wechat_app_secret(self) -> str:
        """Get WeChat App Secret from environment"""
        return os.getenv('WECHAT_APP_SECRET', '')

    @property
    def bilibili_access_key(self) -> str:
        """Get Bilibili Access Key from environment"""
        return os.getenv('BILIBILI_ACCESS_KEY', '')

    @property
    def bilibili_secret_key(self) -> str:
        """Get Bilibili Secret Key from environment"""
        return os.getenv('BILIBILI_SECRET_KEY', '')

    @property
    def storage_path(self) -> str:
        """Get storage base path"""
        return os.getenv('STORAGE_PATH', self.get('storage.base_path', './storage'))

    @property
    def whisper_model(self) -> str:
        """Get Whisper model name"""
        return os.getenv('WHISPER_MODEL', self.get('whisper.model', 'medium'))

    @property
    def whisper_device(self) -> str:
        """Get Whisper device (cpu/cuda)"""
        return os.getenv('WHISPER_DEVICE', self.get('whisper.device', 'cpu'))


# Global config instance
_config_instance = None


def get_config(config_path: str = "config/config.yaml") -> Config:
    """
    Get global configuration instance

    Args:
        config_path: Path to configuration file

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
