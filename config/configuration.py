"""
Configuration Management System

This module handles environment variables, configuration files, and
system settings for the Multi-Agent Product Listing System.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv
import json

class EnvironmentConfig(BaseSettings):
    """
    Environment-based configuration using Pydantic BaseSettings.
    Automatically loads from environment variables and .env files.
    """

    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    nano_banana_api_key: Optional[str] = Field(None, env="NANO_BANANA_API_KEY") 
    shopify_api_key: Optional[str] = Field(None, env="SHOPIFY_API_KEY")
    shopify_shop_domain: Optional[str] = Field(None, env="SHOPIFY_SHOP_DOMAIN")

    # System Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_concurrent_agents: int = Field(3, env="MAX_CONCURRENT_AGENTS")
    default_timeout: int = Field(300, env="DEFAULT_TIMEOUT")
    enable_caching: bool = Field(True, env="ENABLE_CACHING")
    cache_ttl: int = Field(3600, env="CACHE_TTL")

    # Agent-Specific Settings
    scraping_timeout: int = Field(30, env="SCRAPING_TIMEOUT")
    image_quality_threshold: float = Field(0.7, env="IMAGE_QUALITY_THRESHOLD")
    auto_publish_products: bool = Field(False, env="AUTO_PUBLISH_PRODUCTS")
    pod_enabled: bool = Field(True, env="POD_ENABLED")

    # File Paths
    log_directory: str = Field("logs", env="LOG_DIRECTORY")
    cache_directory: str = Field("cache", env="CACHE_DIRECTORY")
    config_file: Optional[str] = Field(None, env="CONFIG_FILE")

    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class ConfigurationManager:
    """
    Centralized configuration management system.
    Supports environment variables, JSON files, and programmatic configuration.
    """

    def __init__(self, config_file: Optional[str] = None, env_file: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to JSON configuration file
            env_file: Path to .env file
        """
        self.config_file = config_file
        self.env_file = env_file

        # Load environment variables
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
        elif Path(".env").exists():
            load_dotenv(".env")

        # Load base configuration from environment
        self.env_config = EnvironmentConfig()

        # Load and merge file-based configuration
        self.file_config = {}
        if config_file:
            self.file_config = self._load_config_file(config_file)

        # Merge configurations (file overrides environment)
        self.merged_config = self._merge_configs()

    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""

        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_path, 'r') as f:
                return json.load(f) or {}
        except Exception as e:
            raise ValueError(f"Error loading config file {config_file}: {str(e)}")

    def _merge_configs(self) -> Dict[str, Any]:
        """Merge environment and file configurations."""

        # Start with environment config
        merged = self.env_config.dict()

        # Override with file config
        merged.update(self.file_config)

        return merged

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value."""
        return self.merged_config.get(key, default)

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate current configuration and return validation results.

        Returns:
            Dict with validation status and any issues found
        """

        issues = []
        warnings = []

        # Check required API keys based on enabled features
        if not self.merged_config.get('nano_banana_api_key'):
            warnings.append("No nano-banana API key configured - will use mock image generation")

        if not self.merged_config.get('openai_api_key'):
            warnings.append("No OpenAI API key configured - will use basic description enhancement")

        if not self.merged_config.get('shopify_api_key'):
            warnings.append("No Shopify API key configured - e-commerce integration will be limited")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'config_sources': {
                'environment_file': bool(self.env_file),
                'config_file': bool(self.config_file),
                'environment_variables': True
            }
        }

def load_default_configuration():
    """
    Load default system configuration for the multi-agent system.

    Returns:
        Dict with default configuration
    """
    from ..models.data_models import SystemConfig, AgentConfig, AgentType

    # Create default agent configurations
    agent_configs = []

    # Description Generator Agent Config
    desc_config = AgentConfig(
        agent_type=AgentType.DESCRIPTION_GENERATOR,
        enabled=True,
        max_retries=3,
        timeout=300,
        config={
            'scraping_timeout': 30,
            'max_description_length': 5000
        }
    )
    agent_configs.append(desc_config)

    # Image Generator Agent Config  
    img_config = AgentConfig(
        agent_type=AgentType.IMAGE_GENERATOR,
        enabled=True,
        max_retries=2,
        timeout=180,
        config={
            'image_quality_threshold': 0.7,
            'fallback_enabled': True
        }
    )
    agent_configs.append(img_config)

    # E-commerce Integration Agent Config
    ecom_config = AgentConfig(
        agent_type=AgentType.ECOMMERCE_INTEGRATOR,
        enabled=True,
        max_retries=2,
        timeout=120,
        config={
            'auto_publish': False,
            'pod_enabled': True
        }
    )
    agent_configs.append(ecom_config)

    # Create system config
    system_config = SystemConfig(
        max_concurrent_agents=3,
        default_timeout=300,
        log_level="INFO",
        enable_caching=True,
        cache_ttl=3600,
        agent_configs=agent_configs
    )

    return system_config

def create_sample_env_file(output_path: str = ".env.sample") -> None:
    """Create a sample .env file with all environment variables."""

    sample_env_content = """# Multi-Agent Product Listing System Configuration

# API Keys (replace with your actual keys)
OPENAI_API_KEY=your-openai-key-here
NANO_BANANA_API_KEY=your-nano-banana-key-here
SHOPIFY_API_KEY=your-shopify-private-app-key
SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com

# System Settings
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=3
DEFAULT_TIMEOUT=300
ENABLE_CACHING=true
CACHE_TTL=3600

# Agent Settings
SCRAPING_TIMEOUT=30
IMAGE_QUALITY_THRESHOLD=0.7
AUTO_PUBLISH_PRODUCTS=false
POD_ENABLED=true

# File Paths
LOG_DIRECTORY=logs
CACHE_DIRECTORY=cache
"""

    with open(output_path, 'w') as f:
        f.write(sample_env_content)

    print(f"Sample environment file created: {output_path}")
