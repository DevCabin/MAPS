"""
Configuration management for the Multi-Agent Product Listing System

Handles environment variables, API keys, and system settings with support for
Replicate API integration for nano-banana image generation.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Config:
    """
    Main configuration class for the multi-agent system.

    Loads configuration from environment variables and provides
    typed access to all system settings.
    """

    # API Configuration
    replicate_api_token: str = field(default_factory=lambda: os.getenv("REPLICATE_API_TOKEN", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    shopify_api_key: str = field(default_factory=lambda: os.getenv("SHOPIFY_API_KEY", ""))
    shopify_secret: str = field(default_factory=lambda: os.getenv("SHOPIFY_SECRET", ""))
    shopify_store_url: str = field(default_factory=lambda: os.getenv("SHOPIFY_STORE_URL", ""))

    # Image Generation Settings (Replicate nano-banana)
    image_width: int = field(default_factory=lambda: int(os.getenv("IMAGE_WIDTH", "1024")))
    image_height: int = field(default_factory=lambda: int(os.getenv("IMAGE_HEIGHT", "1024")))
    image_steps: int = field(default_factory=lambda: int(os.getenv("IMAGE_STEPS", "20")))
    image_guidance: float = field(default_factory=lambda: float(os.getenv("IMAGE_GUIDANCE", "7.5")))

    # System Configuration
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("TIMEOUT_SECONDS", "300")))

    # Agent Configuration
    description_agent_enabled: bool = field(default_factory=lambda: os.getenv("DESCRIPTION_AGENT_ENABLED", "true").lower() == "true")
    image_agent_enabled: bool = field(default_factory=lambda: os.getenv("IMAGE_AGENT_ENABLED", "true").lower() == "true")
    ecommerce_agent_enabled: bool = field(default_factory=lambda: os.getenv("ECOMMERCE_AGENT_ENABLED", "true").lower() == "true")

    # Web Scraping Configuration
    user_agent: str = field(default_factory=lambda: os.getenv("USER_AGENT", "MultiAgentProductSystem/1.0"))
    scraping_timeout: int = field(default_factory=lambda: int(os.getenv("SCRAPING_TIMEOUT", "30")))

    # Database/Storage Configuration  
    storage_path: str = field(default_factory=lambda: os.getenv("STORAGE_PATH", "./data"))
    cache_enabled: bool = field(default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() == "true")

    # Deployment Configuration
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug_mode: bool = field(default_factory=lambda: os.getenv("DEBUG_MODE", "false").lower() == "true")

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
        self._setup_storage()

    def _validate_config(self):
        """Validate required configuration parameters."""
        errors = []

        # Validate Replicate API token
        if self.image_agent_enabled and not self.replicate_api_token:
            errors.append("REPLICATE_API_TOKEN is required when image generation is enabled")

        # Validate image generation parameters
        if self.image_width < 64 or self.image_width > 2048:
            errors.append("IMAGE_WIDTH must be between 64 and 2048")

        if self.image_height < 64 or self.image_height > 2048:
            errors.append("IMAGE_HEIGHT must be between 64 and 2048")

        if self.image_steps < 1 or self.image_steps > 100:
            errors.append("IMAGE_STEPS must be between 1 and 100")

        if self.image_guidance < 0 or self.image_guidance > 20:
            errors.append("IMAGE_GUIDANCE must be between 0 and 20")

        # Validate Shopify configuration
        if self.ecommerce_agent_enabled:
            if not self.shopify_api_key:
                errors.append("SHOPIFY_API_KEY is required when e-commerce integration is enabled")
            if not self.shopify_secret:
                errors.append("SHOPIFY_SECRET is required when e-commerce integration is enabled")
            if not self.shopify_store_url:
                errors.append("SHOPIFY_STORE_URL is required when e-commerce integration is enabled")

        # Validate system parameters
        if self.max_retries < 0 or self.max_retries > 10:
            errors.append("MAX_RETRIES must be between 0 and 10")

        if self.timeout_seconds < 10 or self.timeout_seconds > 3600:
            errors.append("TIMEOUT_SECONDS must be between 10 and 3600")

        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

    def _setup_storage(self):
        """Create storage directories if they don't exist."""
        storage_path = Path(self.storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (storage_path / "logs").mkdir(exist_ok=True)
        (storage_path / "cache").mkdir(exist_ok=True)
        (storage_path / "images").mkdir(exist_ok=True)
        (storage_path / "products").mkdir(exist_ok=True)

    @classmethod
    def from_env_file(cls, env_file_path: str = ".env"):
        """
        Load configuration from an environment file.

        Args:
            env_file_path: Path to the environment file

        Returns:
            Config instance loaded from file
        """
        env_path = Path(env_file_path)
        if env_path.exists():
            # Simple env file parser
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"'')

        return cls()

    def get_replicate_config(self) -> Dict[str, Any]:
        """
        Get Replicate-specific configuration.

        Returns:
            Dictionary with Replicate settings
        """
        return {
            "api_token": self.replicate_api_token,
            "model": "google/nano-banana",
            "version": "626c4a4543e3dc7c19e2303cd1f30ae4b3fc9604a5b8dac19f1e0194ad468560",
            "default_params": {
                "width": self.image_width,
                "height": self.image_height,
                "num_inference_steps": self.image_steps,
                "guidance_scale": self.image_guidance
            }
        }

    def get_shopify_config(self) -> Dict[str, Any]:
        """
        Get Shopify-specific configuration.

        Returns:
            Dictionary with Shopify settings
        """
        return {
            "api_key": self.shopify_api_key,
            "secret": self.shopify_secret,
            "store_url": self.shopify_store_url,
            "api_version": "2023-10"
        }

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get agent-specific configuration.

        Args:
            agent_name: Name of the agent

        Returns:
            Dictionary with agent-specific settings
        """
        base_config = {
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "log_level": self.log_level
        }

        if agent_name.lower() == "imagegeneration":
            base_config.update(self.get_replicate_config())
        elif agent_name.lower() == "ecommerce":
            base_config.update(self.get_shopify_config())

        return base_config

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        config_dict = {}
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            # Mask sensitive values
            if "token" in field_name.lower() or "key" in field_name.lower() or "secret" in field_name.lower():
                if value:
                    config_dict[field_name] = f"{value[:8]}***"
                else:
                    config_dict[field_name] = "Not set"
            else:
                config_dict[field_name] = value

        return config_dict

# Global configuration instance
_config_instance: Optional[Config] = None

def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def initialize_config(env_file: str = ".env") -> Config:
    """
    Initialize configuration from environment file.

    Args:
        env_file: Path to environment file

    Returns:
        Initialized Config instance
    """
    global _config_instance
    _config_instance = Config.from_env_file(env_file)
    return _config_instance

def reset_config():
    """Reset the global configuration instance."""
    global _config_instance
    _config_instance = None
