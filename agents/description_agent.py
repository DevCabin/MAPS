"""
Stage 1 Agent: Product Description Generator

This agent handles web scraping from product URLs and generates enhanced
product descriptions using AI/LLM integration.
"""

import asyncio
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import aiohttp
import json

from .base_agent import BaseAgent, AgentException
from ..models.data_models import (
    AgentType, ScrapedProductData, EnhancedProductDescription, AgentConfig
)

class ProductDescriptionAgent(BaseAgent):
    """
    Agent responsible for:
    1. Web scraping product data from URLs
    2. Generating enhanced product descriptions using AI
    3. SEO optimization and keyword extraction
    """

    def _get_stage_number(self) -> int:
        """Return stage 1 for product description generation."""
        return 1

    def _initialize(self) -> None:
        """Initialize web scraping and AI resources."""
        self.session = None
        self.openai_api_key = self.config.config.get("openai_api_key")
        self.scraping_timeout = self.config.config.get("scraping_timeout", 30)
        self.max_description_length = self.config.config.get("max_description_length", 5000)

        # Common web scraping selectors for different e-commerce platforms
        self.selectors = {
            "title": [
                "h1", "[data-testid='product-title']", ".product-title", 
                "#product-title", ".pdp-product-name", "[class*='product-name']"
            ],
            "description": [
                "[data-testid='product-description']", ".product-description", 
                "#product-description", ".description", "[class*='description']",
                ".product-details", "[class*='details']"
            ],
            "price": [
                "[data-testid='price']", ".price", "#price", "[class*='price']",
                ".product-price", "[class*='product-price']"
            ],
            "features": [
                ".features li", ".product-features li", "[class*='feature'] li",
                ".specifications li", ".specs li"
            ],
            "images": [
                ".product-images img", ".gallery img", "[class*='product-image'] img"
            ]
        }

    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data contains URL or description."""
        url = input_data.get("product_url")
        description = input_data.get("product_description")
        title = input_data.get("product_title")

        if not any([url, description, title]):
            raise AgentException(
                "At least one of product_url, product_description, or product_title required",
                self.agent_type
            )

        if url:
            parsed = urlparse(str(url))
            if not all([parsed.scheme, parsed.netloc]):
                raise AgentException("Invalid URL format", self.agent_type)

        return True

    def _validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output contains enhanced description."""
        required_fields = ["title", "short_description", "detailed_description", "key_features"]

        for field in required_fields:
            if field not in output_data:
                raise AgentException(f"Missing required field: {field}", self.agent_type)

        if len(output_data.get("key_features", [])) < 3:
            raise AgentException("At least 3 key features required", self.agent_type)

        return True

    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution logic for product description generation."""

        # Step 1: Gather product data
        scraped_data = None
        if input_data.get("product_url"):
            self.logger.info(f"Scraping product data from URL: {input_data['product_url']}")
            scraped_data = await self._scrape_product_data(input_data["product_url"])

        # Step 2: Compile available information
        product_info = self._compile_product_info(input_data, scraped_data)

        # Step 3: Generate enhanced description
        self.logger.info("Generating enhanced product description")
        enhanced_description = await self._generate_enhanced_description(product_info)

        # Step 4: Format result
        result = {
            "title": enhanced_description.title,
            "short_description": enhanced_description.short_description,
            "detailed_description": enhanced_description.detailed_description,
            "key_features": enhanced_description.key_features,
            "seo_keywords": enhanced_description.seo_keywords,
            "target_audience": enhanced_description.target_audience,
            "use_cases": enhanced_description.use_cases,
            "benefits": enhanced_description.benefits,
            "scraped_data": scraped_data.dict() if scraped_data else None
        }

        return result

    async def _scrape_product_data(self, url: str) -> Optional[ScrapedProductData]:
        """Scrape product data from the given URL."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(self.scraping_timeout)) as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        self.logger.warning(f"HTTP {response.status} when scraping {url}")
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract product data using selectors
                    scraped_data = ScrapedProductData()

                    # Title
                    scraped_data.title = self._extract_text(soup, self.selectors["title"])

                    # Description
                    scraped_data.description = self._extract_text(soup, self.selectors["description"])

                    # Price
                    price_text = self._extract_text(soup, self.selectors["price"])
                    if price_text:
                        scraped_data.price, scraped_data.currency = self._parse_price(price_text)

                    # Features
                    scraped_data.features = self._extract_list(soup, self.selectors["features"])

                    # Images
                    scraped_data.images = self._extract_images(soup, self.selectors["images"], url)

                    # Additional metadata
                    scraped_data.category = self._extract_category(soup)
                    scraped_data.brand = self._extract_brand(soup)
                    scraped_data.availability = self._extract_availability(soup)

                    return scraped_data

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def _extract_text(self, soup: BeautifulSoup, selectors: list) -> Optional[str]:
        """Extract text using multiple selectors."""
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) > 5:  # Minimum meaningful text
                    return text
        return None

    def _extract_list(self, soup: BeautifulSoup, selectors: list) -> list:
        """Extract list items using selectors."""
        items = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and text not in items:
                    items.append(text)
        return items

    def _extract_images(self, soup: BeautifulSoup, selectors: list, base_url: str) -> list:
        """Extract image URLs."""
        images = []
        for selector in selectors:
            elements = soup.select(selector)
            for img in elements:
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(base_url, src)
                    if full_url not in images:
                        images.append(full_url)
        return images

    def _parse_price(self, price_text: str) -> tuple:
        """Parse price and currency from text."""
        # Remove common formatting
        clean_text = re.sub(r'[^\d.,\$€£¥]', ' ', price_text)

        # Extract currency symbols
        currency_symbols = {'$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY'}
        currency = None
        for symbol, code in currency_symbols.items():
            if symbol in price_text:
                currency = code
                break

        # Extract numeric value
        numbers = re.findall(r'\d+[.,]?\d*', clean_text)
        if numbers:
            try:
                price_val = float(numbers[0].replace(',', ''))
                return price_val, currency
            except ValueError:
                pass

        return None, currency

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product category."""
        category_selectors = [
            ".breadcrumb a:last-child", ".category", "[class*='category']",
            ".product-category", "[data-testid='category']"
        ]
        return self._extract_text(soup, category_selectors)

    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product brand."""
        brand_selectors = [
            ".brand", "[class*='brand']", ".manufacturer", 
            "[data-testid='brand']", "[class*='manufacturer']"
        ]
        return self._extract_text(soup, brand_selectors)

    def _extract_availability(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract availability status."""
        availability_selectors = [
            ".availability", "[class*='availability']", ".stock-status",
            "[class*='stock']", "[data-testid='availability']"
        ]
        return self._extract_text(soup, availability_selectors)

    def _compile_product_info(self, input_data: Dict[str, Any], scraped_data: Optional[ScrapedProductData]) -> Dict[str, Any]:
        """Compile all available product information."""
        info = {}

        # From input data
        for key in ["product_title", "product_description", "product_category", "brand", "price"]:
            if input_data.get(key):
                info[key] = input_data[key]

        # From scraped data
        if scraped_data:
            if scraped_data.title:
                info["scraped_title"] = scraped_data.title
            if scraped_data.description:
                info["scraped_description"] = scraped_data.description
            if scraped_data.features:
                info["scraped_features"] = scraped_data.features
            if scraped_data.category:
                info["scraped_category"] = scraped_data.category
            if scraped_data.brand:
                info["scraped_brand"] = scraped_data.brand

        return info

    async def _generate_enhanced_description(self, product_info: Dict[str, Any]) -> EnhancedProductDescription:
        """Generate enhanced description using AI/mock generation."""

        # For this example, we'll create a sophisticated mock generation
        # In production, this would integrate with OpenAI or similar service

        # Determine the best title
        title = (
            product_info.get("product_title") or 
            product_info.get("scraped_title") or 
            "Premium Product"
        )

        # Generate descriptions based on available info
        base_description = (
            product_info.get("product_description") or 
            product_info.get("scraped_description") or 
            "High-quality product designed for optimal performance"
        )

        # Extract or generate features
        features = product_info.get("scraped_features", [])
        if len(features) < 3:
            features.extend([
                "Premium quality construction",
                "User-friendly design", 
                "Excellent durability",
                "Versatile functionality",
                "Great value for money"
            ])

        # Generate SEO keywords
        keywords = self._generate_seo_keywords(title, base_description, features)

        # Create enhanced description
        enhanced = EnhancedProductDescription(
            title=title,
            short_description=f"{base_description[:200]}..." if len(base_description) > 200 else base_description,
            detailed_description=self._expand_description(base_description, features),
            key_features=features[:8],  # Top 8 features
            seo_keywords=keywords,
            target_audience=self._determine_target_audience(title, base_description),
            use_cases=self._generate_use_cases(title, features),
            benefits=self._generate_benefits(features)
        )

        return enhanced

    def _generate_seo_keywords(self, title: str, description: str, features: list) -> list:
        """Generate SEO keywords from product information."""
        text = f"{title} {description} {' '.join(features)}".lower()

        # Extract meaningful words (remove common words)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an'}
        words = re.findall(r'\b\w{3,}\b', text)
        keywords = [word for word in words if word not in stop_words]

        # Get unique keywords, prioritize by frequency
        from collections import Counter
        word_counts = Counter(keywords)
        top_keywords = [word for word, count in word_counts.most_common(10)]

        return top_keywords[:8]  # Return top 8 keywords

    def _expand_description(self, base_description: str, features: list) -> str:
        """Create detailed description from base information."""
        expanded = base_description

        if features:
            expanded += "\n\nKey Features:\n"
            for feature in features[:5]:
                expanded += f"• {feature}\n"

        expanded += "\n\nThis product represents excellent value and quality, designed to meet your needs with reliability and performance you can trust."

        return expanded

    def _determine_target_audience(self, title: str, description: str) -> str:
        """Determine target audience based on product information."""
        text = f"{title} {description}".lower()

        if any(word in text for word in ['professional', 'business', 'office']):
            return "Business professionals and office workers"
        elif any(word in text for word in ['home', 'family', 'household']):
            return "Homeowners and families"
        elif any(word in text for word in ['tech', 'digital', 'smart']):
            return "Technology enthusiasts and early adopters"
        else:
            return "General consumers seeking quality products"

    def _generate_use_cases(self, title: str, features: list) -> list:
        """Generate use cases based on product information."""
        use_cases = []
        text = f"{title} {' '.join(features)}".lower()

        if 'portable' in text or 'mobile' in text:
            use_cases.append("On-the-go usage")
        if 'home' in text or 'household' in text:
            use_cases.append("Home and personal use")
        if 'professional' in text or 'business' in text:
            use_cases.append("Professional and business applications")
        if 'outdoor' in text or 'travel' in text:
            use_cases.append("Outdoor and travel scenarios")

        if not use_cases:
            use_cases = ["Daily use", "Special occasions", "Gift giving"]

        return use_cases

    def _generate_benefits(self, features: list) -> list:
        """Generate benefits from features."""
        benefits = []
        for feature in features[:5]:
            if 'quality' in feature.lower():
                benefits.append("Long-lasting reliability")
            elif 'easy' in feature.lower() or 'user-friendly' in feature.lower():
                benefits.append("Effortless user experience")
            elif 'fast' in feature.lower() or 'quick' in feature.lower():
                benefits.append("Time-saving efficiency")
            else:
                benefits.append(f"Enhanced performance through {feature.lower()}")

        return benefits

# Register the agent
from .base_agent import AgentFactory
AgentFactory.register_agent(AgentType.DESCRIPTION_GENERATOR, ProductDescriptionAgent)
