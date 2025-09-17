"""
Stage 3 Agent: E-commerce Integration Agent

This agent handles formatting and preparing product listings for
e-commerce platforms, particularly Shopify, with proper data structure
and validation.
"""

import asyncio
import re
import html
from typing import Any, Dict, Optional, List
from datetime import datetime
import json

from .base_agent import BaseAgent, AgentException
from ..models.data_models import (
    AgentType, ShopifyProductListing, AgentConfig
)

class EcommerceIntegrationAgent(BaseAgent):
    """
    Agent responsible for:
    1. Formatting product data for Shopify API
    2. Creating SEO-optimized product listings
    3. Generating product variants and options
    4. Validating e-commerce data requirements
    5. Preparing for POD (Print-on-Demand) integration
    """

    def _get_stage_number(self) -> int:
        """Return stage 3 for e-commerce integration."""
        return 3

    def _initialize(self) -> None:
        """Initialize e-commerce integration resources."""
        self.shopify_api_key = self.config.config.get("shopify_api_key")
        self.shopify_shop_domain = self.config.config.get("shopify_shop_domain")
        self.default_vendor = self.config.config.get("default_vendor", "Your Store")
        self.auto_publish = self.config.config.get("auto_publish", False)

        # SEO optimization settings
        self.max_title_length = self.config.config.get("max_title_length", 70)
        self.max_description_length = self.config.config.get("max_description_length", 155)
        self.include_structured_data = self.config.config.get("include_structured_data", True)

        # Product categorization
        self.category_mappings = self.config.config.get("category_mappings", {})
        self.default_product_type = self.config.config.get("default_product_type", "General")

        # POD integration settings
        self.pod_enabled = self.config.config.get("pod_enabled", True)
        self.default_print_provider = self.config.config.get("default_print_provider", "printful")

        # Default product options for POD
        self.default_variants = [
            {"option1": "Small", "price": "19.99", "sku": "PROD-S"},
            {"option1": "Medium", "price": "24.99", "sku": "PROD-M"},
            {"option1": "Large", "price": "29.99", "sku": "PROD-L"},
            {"option1": "X-Large", "price": "34.99", "sku": "PROD-XL"}
        ]

    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data contains required product information."""
        required_fields = ["title", "detailed_description"]

        for field in required_fields:
            if not input_data.get(field):
                raise AgentException(f"Missing required field for e-commerce: {field}", self.agent_type)

        # Validate title length
        title = input_data.get("title", "")
        if len(title) < 10 or len(title) > 255:
            raise AgentException("Product title must be between 10 and 255 characters", self.agent_type)

        return True

    def _validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output contains properly formatted Shopify listing."""
        required_fields = ["title", "body_html", "handle", "seo_title", "seo_description"]

        for field in required_fields:
            if field not in output_data:
                raise AgentException(f"Missing required Shopify field: {field}", self.agent_type)

        # Validate Shopify-specific constraints
        if len(output_data.get("title", "")) > 255:
            raise AgentException("Shopify title exceeds 255 character limit", self.agent_type)

        return True

    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution logic for e-commerce integration."""

        # Step 1: Create Shopify-compatible product listing
        self.logger.info("Creating Shopify product listing")
        shopify_listing = await self._create_shopify_listing(input_data)

        # Step 2: Generate SEO optimizations
        self.logger.info("Optimizing SEO elements")
        shopify_listing = await self._optimize_seo(shopify_listing, input_data)

        # Step 3: Add product variants for POD
        if self.pod_enabled:
            self.logger.info("Adding POD product variants")
            shopify_listing = await self._add_pod_variants(shopify_listing, input_data)

        # Step 4: Format final result
        result = {
            "title": shopify_listing.title,
            "body_html": shopify_listing.body_html,
            "vendor": shopify_listing.vendor,
            "product_type": shopify_listing.product_type,
            "tags": shopify_listing.tags,
            "published": shopify_listing.published,
            "handle": shopify_listing.handle,
            "images": shopify_listing.images,
            "variants": shopify_listing.variants,
            "options": shopify_listing.options,
            "seo_title": shopify_listing.seo_title,
            "seo_description": shopify_listing.seo_description,
            "shopify_ready": True
        }

        return result

    async def _create_shopify_listing(self, input_data: Dict[str, Any]) -> ShopifyProductListing:
        """Create base Shopify product listing from input data."""

        # Create product handle (URL slug)
        handle = self._create_product_handle(input_data["title"])

        # Format product description as HTML
        body_html = self._format_product_html(input_data)

        # Determine product type and vendor
        product_type = self._determine_product_type(input_data)
        vendor = input_data.get("brand") or self.default_vendor

        # Create tags from keywords and features
        tags = self._generate_product_tags(input_data)

        # Prepare images array
        images = self._format_images(input_data)

        shopify_listing = ShopifyProductListing(
            title=input_data["title"],
            body_html=body_html,
            vendor=vendor,
            product_type=product_type,
            tags=tags,
            published=self.auto_publish,
            handle=handle,
            images=images
        )

        return shopify_listing

    def _create_product_handle(self, title: str) -> str:
        """Create Shopify-compatible product handle from title."""

        # Convert to lowercase and replace spaces with hyphens
        handle = title.lower()

        # Remove special characters except hyphens
        handle = re.sub(r'[^a-z0-9\s-]', '', handle)

        # Replace spaces with hyphens
        handle = re.sub(r'\s+', '-', handle)

        # Remove multiple consecutive hyphens
        handle = re.sub(r'-+', '-', handle)

        # Remove leading/trailing hyphens
        handle = handle.strip('-')

        # Ensure handle is not empty and not too long
        if not handle:
            handle = "product"

        if len(handle) > 100:
            handle = handle[:100].rstrip('-')

        return handle

    def _format_product_html(self, input_data: Dict[str, Any]) -> str:
        """Format product information as HTML for Shopify."""

        html_content = []

        # Main description
        description = input_data.get("detailed_description", "")
        if description:
            # Convert line breaks to HTML
            description_html = description.replace('\n', '<br>')
            html_content.append(f"<p>{html.escape(description_html)}</p>")

        # Key features section
        features = input_data.get("key_features", [])
        if features:
            html_content.append("<h3>Key Features:</h3>")
            html_content.append("<ul>")
            for feature in features:
                html_content.append(f"<li>{html.escape(feature)}</li>")
            html_content.append("</ul>")

        # Benefits section
        benefits = input_data.get("benefits", [])
        if benefits:
            html_content.append("<h3>Benefits:</h3>")
            html_content.append("<ul>")
            for benefit in benefits:
                html_content.append(f"<li>{html.escape(benefit)}</li>")
            html_content.append("</ul>")

        # Use cases section
        use_cases = input_data.get("use_cases", [])
        if use_cases:
            html_content.append("<h3>Perfect For:</h3>")
            html_content.append("<ul>")
            for use_case in use_cases:
                html_content.append(f"<li>{html.escape(use_case)}</li>")
            html_content.append("</ul>")

        # Target audience
        target_audience = input_data.get("target_audience")
        if target_audience:
            html_content.append(f"<p><strong>Designed for:</strong> {html.escape(target_audience)}</p>")

        return '\n'.join(html_content)

    def _determine_product_type(self, input_data: Dict[str, Any]) -> str:
        """Determine product type based on available information."""

        # Check for explicit category mapping
        category = input_data.get("product_category") or input_data.get("scraped_category")
        if category and category in self.category_mappings:
            return self.category_mappings[category]

        # Analyze product title and description for type hints
        text = f"{input_data.get('title', '')} {input_data.get('short_description', '')}".lower()

        type_keywords = {
            "Apparel": ["shirt", "t-shirt", "hoodie", "jacket", "dress", "pants", "clothing"],
            "Accessories": ["bag", "wallet", "watch", "jewelry", "hat", "scarf", "belt"],
            "Electronics": ["phone", "computer", "tablet", "headphones", "charger", "cable"],
            "Home & Garden": ["furniture", "decor", "kitchen", "bathroom", "garden", "lighting"],
            "Sports & Fitness": ["fitness", "sport", "exercise", "gym", "outdoor", "running"],
            "Books & Media": ["book", "ebook", "magazine", "dvd", "music", "media"],
            "Health & Beauty": ["skincare", "makeup", "health", "beauty", "wellness", "care"]
        }

        for product_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return product_type

        return self.default_product_type

    def _generate_product_tags(self, input_data: Dict[str, Any]) -> List[str]:
        """Generate product tags from keywords and features."""

        tags = set()

        # Add SEO keywords
        seo_keywords = input_data.get("seo_keywords", [])
        for keyword in seo_keywords:
            # Clean and add keyword
            clean_keyword = keyword.strip().lower()
            if len(clean_keyword) > 2:
                tags.add(clean_keyword)

        # Add product type as tag
        product_type = self._determine_product_type(input_data)
        tags.add(product_type.lower())

        # Add brand as tag
        brand = input_data.get("brand")
        if brand:
            tags.add(brand.lower())

        # Add category tags
        category = input_data.get("product_category") or input_data.get("scraped_category")
        if category:
            tags.add(category.lower())

        # Add feature-based tags
        features = input_data.get("key_features", [])
        for feature in features[:5]:  # Limit to top 5 features
            # Extract meaningful words from features
            words = re.findall(r'\b\w{4,}\b', feature.lower())
            for word in words:
                if word not in {"with", "that", "this", "your", "their"}:
                    tags.add(word)

        # Convert to list and limit to reasonable number
        tag_list = list(tags)[:20]  # Shopify recommends max 20 tags

        return tag_list

    def _format_images(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format images for Shopify listing."""

        images = []

        # Add generated image if available
        image_url = input_data.get("image_url")
        if image_url:
            images.append({
                "src": image_url,
                "alt": input_data.get("title", "Product Image"),
                "position": 1
            })

        # Add scraped images if available
        scraped_data = input_data.get("scraped_data")
        if scraped_data and isinstance(scraped_data, dict):
            scraped_images = scraped_data.get("images", [])
            for idx, img_url in enumerate(scraped_images[:4]):  # Max 5 images total
                images.append({
                    "src": img_url,
                    "alt": f"{input_data.get('title', 'Product')} - Image {idx + 2}",
                    "position": idx + 2
                })

        return images

    async def _optimize_seo(self, listing: ShopifyProductListing, input_data: Dict[str, Any]) -> ShopifyProductListing:
        """Optimize SEO elements for the product listing."""

        # Create SEO-optimized title
        base_title = listing.title
        seo_title = self._create_seo_title(base_title, input_data)
        listing.seo_title = seo_title

        # Create meta description
        seo_description = self._create_seo_description(input_data)
        listing.seo_description = seo_description

        # Add meta fields if enabled
        if self.include_structured_data:
            listing.metafields_global_title_tag = seo_title
            listing.metafields_global_description_tag = seo_description

        return listing

    def _create_seo_title(self, base_title: str, input_data: Dict[str, Any]) -> str:
        """Create SEO-optimized title."""

        # Start with base title
        seo_title = base_title

        # Add primary keyword if not already included
        keywords = input_data.get("seo_keywords", [])
        if keywords:
            primary_keyword = keywords[0]
            if primary_keyword.lower() not in seo_title.lower():
                seo_title = f"{primary_keyword.title()} - {seo_title}"

        # Add brand if available and not included
        brand = input_data.get("brand")
        if brand and brand.lower() not in seo_title.lower():
            seo_title = f"{seo_title} | {brand}"

        # Ensure title is within length limit
        if len(seo_title) > self.max_title_length:
            # Trim while preserving important parts
            seo_title = seo_title[:self.max_title_length - 3] + "..."

        return seo_title

    def _create_seo_description(self, input_data: Dict[str, Any]) -> str:
        """Create SEO-optimized meta description."""

        # Start with short description
        description = input_data.get("short_description", "")

        # Add key features
        features = input_data.get("key_features", [])
        if features and len(description) < 100:
            features_text = ", ".join(features[:3])
            description += f". Features: {features_text}"

        # Add call to action
        if len(description) < 120:
            description += ". Shop now for the best deals!"

        # Ensure description is within length limit
        if len(description) > self.max_description_length:
            description = description[:self.max_description_length - 3] + "..."

        return description

    async def _add_pod_variants(self, listing: ShopifyProductListing, input_data: Dict[str, Any]) -> ShopifyProductListing:
        """Add product variants for Print-on-Demand integration."""

        if not self.pod_enabled:
            return listing

        # Create size options for apparel products
        product_type = listing.product_type.lower()

        if any(keyword in product_type for keyword in ["apparel", "clothing", "shirt"]):
            # Add size variants
            listing.options = [{"name": "Size", "position": 1, "values": ["S", "M", "L", "XL"]}]

            variants = []
            base_price = input_data.get("price", 24.99)

            for idx, size in enumerate(["S", "M", "L", "XL"]):
                variant = {
                    "option1": size,
                    "price": str(base_price + (idx * 2)),  # Incremental pricing
                    "sku": f"{listing.handle.upper()}-{size}",
                    "inventory_management": "shopify",
                    "inventory_policy": "deny",
                    "fulfillment_service": self.default_print_provider,
                    "requires_shipping": True,
                    "taxable": True,
                    "weight": 200,  # grams
                    "weight_unit": "g"
                }
                variants.append(variant)

            listing.variants = variants

        else:
            # Single variant for non-apparel products
            listing.variants = [{
                "price": str(input_data.get("price", 19.99)),
                "sku": listing.handle.upper(),
                "inventory_management": "shopify",
                "inventory_policy": "deny",
                "fulfillment_service": self.default_print_provider,
                "requires_shipping": True,
                "taxable": True
            }]

        return listing

# Register the agent
from .base_agent import AgentFactory
AgentFactory.register_agent(AgentType.ECOMMERCE_INTEGRATOR, EcommerceIntegrationAgent)
