"""
Usage Examples for Multi-Agent Product Listing System with Replicate Integration

This file demonstrates how to use the multi-agent system with Replicate's nano-banana
model for image generation. Updated for Replicate API integration.
"""

import asyncio
import os
from pathlib import Path

async def example_1_basic_usage():
    """
    Basic example: Generate product listing from description using Replicate
    """
    print("=== Example 1: Basic Usage with Replicate ===")

    from multi_agent_product_system import ProductListingOrchestrator
    from multi_agent_product_system.config.configuration import initialize_config

    # Initialize configuration
    config = initialize_config()

    # Create orchestrator
    orchestrator = ProductListingOrchestrator(config)

    # Process product with description
    result = await orchestrator.process_product_listing(
        product_description="Eco-friendly bamboo water bottle with stainless steel cap"
    )

    # Display results
    if result.status == "completed":
        print("✅ Product listing generated successfully!")
        print(f"Description: {result.product_description.enhanced_description[:100]}...")
        print(f"Image URL: {result.product_image.url}")
        print(f"Shopify Ready: {result.shopify_ready}")

        # Output in XML format
        print("\nXML Output:")
        print(result.to_xml())
    else:
        print(f"❌ Failed: {result.error_message}")

async def example_2_custom_image_parameters():
    """
    Example: Custom Replicate image generation parameters
    """
    print("\n=== Example 2: Custom Image Parameters ===")

    from multi_agent_product_system import ProductListingOrchestrator
    from multi_agent_product_system.config.configuration import initialize_config

    config = initialize_config()
    orchestrator = ProductListingOrchestrator(config)

    # Custom image generation settings for Replicate nano-banana
    image_params = {
        "width": 512,
        "height": 512,
        "steps": 30,
        "guidance": 8.0,
        "seed": 42
    }

    result = await orchestrator.process_product_listing(
        product_description="Vintage leather messenger bag",
        image_generation_params=image_params
    )

    if result.status == "completed":
        print("✅ Custom image parameters applied!")
        print(f"Generated with seed {image_params['seed']}")
        print(result.to_xml())

def example_3_configuration_setup():
    """
    Example: Proper configuration setup for Replicate
    """
    print("\n=== Example 3: Configuration Setup ===")

    from multi_agent_product_system.config.configuration import Config

    # Method 1: Environment variables
    os.environ["REPLICATE_API_TOKEN"] = "your_token_here"
    os.environ["IMAGE_WIDTH"] = "1024"
    os.environ["IMAGE_HEIGHT"] = "1024"
    os.environ["IMAGE_STEPS"] = "20"
    os.environ["IMAGE_GUIDANCE"] = "7.5"

    config = Config()
    print("Environment configuration:")
    print(f"- Replicate Token: {'Set' if config.replicate_api_token else 'Not set'}")
    print(f"- Image Size: {config.image_width}x{config.image_height}")
    print(f"- Steps: {config.image_steps}")
    print(f"- Guidance: {config.image_guidance}")

    # Get Replicate configuration
    replicate_config = config.get_replicate_config()
    print("\nReplicate Configuration:")
    print(f"- Model: {replicate_config['model']}")
    print(f"- Version: {replicate_config['version'][:12]}...")
    print(f"- Default Width: {replicate_config['default_params']['width']}")
    print(f"- Default Height: {replicate_config['default_params']['height']}")

async def example_4_error_handling():
    """
    Example: Proper error handling for Replicate integration
    """
    print("\n=== Example 4: Error Handling ===")

    from multi_agent_product_system import ProductListingOrchestrator
    from multi_agent_product_system.config.configuration import Config

    # Test with invalid configuration
    config = Config()
    config.replicate_api_token = ""  # Invalid token

    orchestrator = ProductListingOrchestrator(config)

    try:
        result = await orchestrator.process_product_listing(
            product_description="Test product"
        )

        if result.status == "failed":
            print("❌ Expected failure occurred:")
            print(f"Error: {result.error_message}")
            print("✅ Error handling working correctly!")

    except Exception as e:
        print(f"Exception caught: {str(e)}")

def example_5_replicate_specific_features():
    """
    Example: Replicate-specific features and cost estimation
    """
    print("\n=== Example 5: Replicate Features ===")

    from multi_agent_product_system.config.configuration import initialize_config
    from multi_agent_product_system.agents.image_agent import ImageGenerationAgent

    config = initialize_config()

    # Create image agent to demonstrate Replicate features
    try:
        image_agent = ImageGenerationAgent(config)

        # Cost estimation
        params = {
            "width": 1024,
            "height": 1024, 
            "steps": 20
        }

        estimated_cost = image_agent._get_generation_cost_estimate(params)
        print(f"💰 Estimated cost: ${estimated_cost:.6f} per image")

        print("\n🔧 Replicate nano-banana model features:")
        print("- High-quality image generation")
        print("- Fast generation times")
        print("- Customizable parameters")
        print("- Cost-effective pricing")

    except Exception as e:
        print(f"Could not initialize image agent: {e}")

async def main():
    """
    Main function to run all examples
    """
    print("🚀 Multi-Agent Product Listing System - Replicate Examples")
    print("=" * 60)

    # Check if API token is set
    if not os.getenv("REPLICATE_API_TOKEN"):
        print("⚠️  REPLICATE_API_TOKEN not set!")
        print("Get your token from: https://replicate.com/account/api-tokens")
        print("Set it in your .env file or environment variables")
        print("Example .env file:")
        print("REPLICATE_API_TOKEN=r8_your_token_here")
        print("")

    try:
        # Run examples (some may fail without proper API setup)
        await example_1_basic_usage()
        await example_2_custom_image_parameters()
        example_3_configuration_setup()
        await example_4_error_handling()
        example_5_replicate_specific_features()

        print("\n✅ Examples completed!")
        print("\n📚 Next steps:")
        print("1. Get your Replicate API token from https://replicate.com/account/api-tokens")
        print("2. Set REPLICATE_API_TOKEN in your .env file")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Start building your product listings!")

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure the package is installed: pip install -e .")
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        print("Make sure all dependencies are installed and API tokens are configured")

if __name__ == "__main__":
    asyncio.run(main())
