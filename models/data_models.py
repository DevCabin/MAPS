"""
Data models for the Multi-Agent Product Listing System.

This module defines Pydantic models for type safety, validation, and serialization
across the entire product listing pipeline.
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class StageStatus(str, Enum):
    """Status enumeration for each stage of the pipeline."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class AgentType(str, Enum):
    """Types of agents in the system."""
    DESCRIPTION_GENERATOR = "description_generator"
    IMAGE_GENERATOR = "image_generator"
    ECOMMERCE_INTEGRATOR = "ecommerce_integrator"
    ORCHESTRATOR = "orchestrator"

class ProductInput(BaseModel):
    """Input data for product listing generation."""

    product_url: Optional[HttpUrl] = Field(None, description="URL to scrape product data from")
    product_description: Optional[str] = Field(None, min_length=10, description="Initial product description")
    product_title: Optional[str] = Field(None, min_length=3, description="Product title")
    product_category: Optional[str] = Field(None, description="Product category")
    price: Optional[float] = Field(None, ge=0, description="Product price")
    brand: Optional[str] = Field(None, description="Product brand")
    additional_context: Optional[str] = Field(None, description="Additional context for generation")

    @validator('product_url', 'product_description')
    def at_least_one_input_required(cls, v, values):
        """Ensure at least one input source is provided."""
        if not v and not values.get('product_description') and not values.get('product_title'):
            raise ValueError('Either product_url, product_description, or product_title must be provided')
        return v

class ScrapedProductData(BaseModel):
    """Data scraped from a product URL."""

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    specifications: Dict[str, Any] = Field(default_factory=dict)
    availability: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    scraped_at: datetime = Field(default_factory=datetime.now)

class EnhancedProductDescription(BaseModel):
    """Enhanced product description with SEO optimization."""

    title: str = Field(..., min_length=10, max_length=200)
    short_description: str = Field(..., min_length=50, max_length=500)
    detailed_description: str = Field(..., min_length=100)
    key_features: List[str] = Field(..., min_items=3)
    specifications: Dict[str, str] = Field(default_factory=dict)
    seo_keywords: List[str] = Field(..., min_items=5)
    target_audience: str = Field(..., min_length=20)
    use_cases: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)

class GeneratedImage(BaseModel):
    """Generated product image data."""

    image_url: HttpUrl
    prompt_used: str
    style: Optional[str] = None
    dimensions: tuple[int, int] = Field(default=(1024, 1024))
    format: str = Field(default="PNG")
    generation_model: str = Field(default="nano-banana")
    generated_at: datetime = Field(default_factory=datetime.now)
    quality_score: Optional[float] = Field(None, ge=0, le=1)

class ShopifyProductListing(BaseModel):
    """Shopify-formatted product listing."""

    title: str = Field(..., max_length=255)
    body_html: str
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    published: bool = Field(default=False)
    template_suffix: Optional[str] = None
    metafields_global_title_tag: Optional[str] = None
    metafields_global_description_tag: Optional[str] = None
    handle: Optional[str] = None
    images: List[Dict[str, Any]] = Field(default_factory=list)
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    options: List[Dict[str, Any]] = Field(default_factory=list)
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

class AgentResult(BaseModel):
    """Result from an individual agent execution."""

    agent_type: AgentType
    stage: int
    status: StageStatus
    data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    retry_count: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PipelineResult(BaseModel):
    """Complete pipeline execution result."""

    pipeline_id: str
    input_data: ProductInput
    stage_results: List[AgentResult] = Field(default_factory=list)
    final_status: StageStatus
    product_description: Optional[EnhancedProductDescription] = None
    generated_image: Optional[GeneratedImage] = None
    shopify_listing: Optional[ShopifyProductListing] = None
    total_execution_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_summary: List[str] = Field(default_factory=list)

class AgentConfig(BaseModel):
    """Configuration for individual agents."""

    agent_type: AgentType
    enabled: bool = Field(default=True)
    max_retries: int = Field(default=3, ge=0)
    timeout: int = Field(default=300, ge=30)  # seconds
    config: Dict[str, Any] = Field(default_factory=dict)

class SystemConfig(BaseModel):
    """System-wide configuration."""

    openai_api_key: Optional[str] = None
    nano_banana_api_key: Optional[str] = None
    shopify_api_key: Optional[str] = None
    shopify_shop_domain: Optional[str] = None
    max_concurrent_agents: int = Field(default=3, ge=1)
    default_timeout: int = Field(default=300, ge=30)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    enable_caching: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=60)  # seconds
    agent_configs: List[AgentConfig] = Field(default_factory=list)
