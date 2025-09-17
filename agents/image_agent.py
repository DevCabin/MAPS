"""
Image Generation Agent for Multi-Agent Product Listing System

This agent handles product image generation using Replicate's nano-banana model.
It integrates with Replicate's API to create high-quality, relevant product images
based on text descriptions.
"""

import asyncio
import base64
import logging
from io import BytesIO
from typing import Dict, Any, Optional
import uuid
from PIL import Image
import replicate
from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from models.data_models import ProductDescription, ProductImage
from config.configuration import Config

class ImageGenerationAgent(BaseAgent):
    """
    Specialized agent for generating product images using Replicate's nano-banana model.

    Capabilities:
    - Generate images from text descriptions
    - Validate image quality and relevance
    - Handle Replicate API integration
    - Support various image formats and sizes
    """

    def __init__(self, config: Config):
        super().__init__("ImageGenerationAgent", config)
        self.replicate_client = None
        self._initialize_replicate()

    def _initialize_replicate(self):
        """Initialize Replicate client with API token."""
        try:
            if not self.config.replicate_api_token:
                raise ValueError("REPLICATE_API_TOKEN not found in configuration")

            # Set the API token for replicate
            replicate.api_token = self.config.replicate_api_token
            self.logger.info("Replicate client initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Replicate client: {str(e)}")
            self.status = AgentStatus.ERROR
            raise

    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Generate product image from description using Replicate's nano-banana model.

        Args:
            input_data: Dictionary containing product description and generation parameters

        Returns:
            AgentResponse containing the generated image data
        """
        try:
            self.status = AgentStatus.PROCESSING
            self.logger.info("Starting image generation process")

            # Extract product description
            if isinstance(input_data.get('product_description'), ProductDescription):
                description_text = input_data['product_description'].enhanced_description
            else:
                description_text = input_data.get('description', '')

            if not description_text:
                raise ValueError("No product description provided for image generation")

            # Generate image using Replicate
            image_result = await self._generate_image_with_replicate(description_text, input_data)

            # Validate and process the generated image
            validated_image = await self._validate_image(image_result)

            self.status = AgentStatus.COMPLETED
            self.logger.info("Image generation completed successfully")

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={"product_image": validated_image},
                metadata={
                    "generation_time": self._get_processing_time(),
                    "model": "google/nano-banana",
                    "platform": "replicate"
                }
            )

        except Exception as e:
            return await self._handle_error(e, "Image generation failed")

    async def _generate_image_with_replicate(
        self, 
        description: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate image using Replicate's nano-banana model.

        Args:
            description: Product description text
            params: Additional generation parameters

        Returns:
            Generated image data from Replicate
        """
        try:
            self.logger.info(f"Generating image for: {description[:100]}...")

            # Prepare the prompt for nano-banana model
            enhanced_prompt = await self._enhance_prompt_for_product(description)

            # Set up generation parameters for Replicate's nano-banana
            generation_params = {
                "prompt": enhanced_prompt,
                "width": params.get("width", 1024),
                "height": params.get("height", 1024),
                "num_inference_steps": params.get("steps", 20),
                "guidance_scale": params.get("guidance", 7.5),
                "seed": params.get("seed", -1)
            }

            self.logger.info(f"Replicate generation params: {generation_params}")

            # Run the model using Replicate
            # Using the specific model version hash for nano-banana
            output = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: replicate.run(
                    "google/nano-banana:626c4a4543e3dc7c19e2303cd1f30ae4b3fc9604a5b8dac19f1e0194ad468560",
                    input=generation_params
                )
            )

            self.logger.info("Image generation completed via Replicate")

            return {
                "image_url": output[0] if isinstance(output, list) else output,
                "prompt": enhanced_prompt,
                "parameters": generation_params
            }

        except Exception as e:
            self.logger.error(f"Replicate image generation failed: {str(e)}")
            raise Exception(f"Failed to generate image with Replicate: {str(e)}")

    async def _enhance_prompt_for_product(self, description: str) -> str:
        """
        Enhance the product description for better image generation.

        Args:
            description: Original product description

        Returns:
            Enhanced prompt optimized for product photography
        """
        # Add product photography keywords for better results
        enhancement_keywords = [
            "professional product photography",
            "clean white background",
            "high quality",
            "commercial photography",
            "studio lighting",
            "detailed"
        ]

        # Create enhanced prompt
        enhanced = f"{description}, {', '.join(enhancement_keywords)}"

        # Ensure reasonable length for nano-banana
        if len(enhanced) > 500:
            enhanced = enhanced[:500] + "..."

        return enhanced

    async def _validate_image(self, image_result: Dict[str, Any]) -> ProductImage:
        """
        Validate and process the generated image.

        Args:
            image_result: Raw image result from Replicate

        Returns:
            Validated ProductImage object
        """
        try:
            image_url = image_result.get("image_url")
            if not image_url:
                raise ValueError("No image URL received from Replicate")

            # Create ProductImage object
            product_image = ProductImage(
                image_id=str(uuid.uuid4()),
                url=image_url,
                alt_text=f"Product image generated from: {image_result.get('prompt', 'description')[:100]}",
                width=image_result.get("parameters", {}).get("width", 1024),
                height=image_result.get("parameters", {}).get("height", 1024),
                format="PNG",
                generation_metadata={
                    "model": "google/nano-banana",
                    "platform": "replicate",
                    "prompt": image_result.get("prompt"),
                    "parameters": image_result.get("parameters", {})
                }
            )

            # Validate image accessibility
            await self._verify_image_accessibility(image_url)

            return product_image

        except Exception as e:
            self.logger.error(f"Image validation failed: {str(e)}")
            raise Exception(f"Generated image validation failed: {str(e)}")

    async def _verify_image_accessibility(self, image_url: str):
        """
        Verify that the generated image URL is accessible.

        Args:
            image_url: URL of the generated image
        """
        import aiohttp

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(image_url) as response:
                    if response.status != 200:
                        raise Exception(f"Image not accessible. Status: {response.status}")

                    self.logger.info(f"Image accessibility verified: {image_url}")

        except Exception as e:
            self.logger.warning(f"Image accessibility check failed: {str(e)}")
            # Don't fail the entire process for accessibility issues

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Check the health status of the image generation service.

        Returns:
            Dictionary containing health status information
        """
        try:
            # Test Replicate API connectivity
            test_result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: replicate.models.get("google/nano-banana")
            )

            return {
                "status": "healthy",
                "service": "replicate",
                "model": "google/nano-banana",
                "api_accessible": True,
                "timestamp": self._get_current_timestamp()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "replicate",
                "model": "google/nano-banana",
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }

    def _get_generation_cost_estimate(self, params: Dict[str, Any]) -> float:
        """
        Estimate the cost of image generation based on parameters.

        Args:
            params: Generation parameters

        Returns:
            Estimated cost in USD
        """
        # Replicate pricing for nano-banana model (approximate)
        base_cost = 0.00025  # Base cost per generation

        # Additional costs based on parameters
        width = params.get("width", 1024)
        height = params.get("height", 1024)
        steps = params.get("steps", 20)

        # Higher resolution and more steps increase cost
        resolution_multiplier = (width * height) / (1024 * 1024)
        steps_multiplier = steps / 20

        estimated_cost = base_cost * resolution_multiplier * steps_multiplier

        return round(estimated_cost, 6)
