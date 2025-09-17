"""
Example Usage and Test Cases for Multi-Agent Product Listing System

This module provides comprehensive examples demonstrating how to use
the multi-agent system for automated product listing generation.
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime

# Example 1: Basic usage with product description
async def example_basic_description():
    """
    Example: Create product listing from title and description.
    """

    print("🚀 Example 1: Basic Product Description to Listing")
    print("=" * 50)

    # Import required modules
    from ..config.configuration import load_default_configuration
    from ..orchestrator import ProductListingOrchestrator
    from ..models.data_models import ProductInput

    # Load configuration
    config = load_default_configuration()

    # Create orchestrator
    orchestrator = ProductListingOrchestrator(config)

    # Create product input
    product_input = ProductInput(
        product_title="Premium Wireless Bluetooth Headphones",
        product_description="High-quality wireless headphones with noise cancellation, 30-hour battery life, and premium sound quality. Perfect for music lovers and professionals.",
        brand="AudioTech",
        price=199.99,
        product_category="Electronics"
    )

    try:
        # Execute pipeline
        print("⏳ Executing multi-agent pipeline...")
        start_time = datetime.now()

        result = await orchestrator.execute_pipeline(product_input)

        execution_time = (datetime.now() - start_time).total_seconds()

        # Display results
        print(f"✅ Pipeline completed in {execution_time:.2f} seconds")
        print(f"📊 Status: {result.final_status.value}")
        print(f"🔧 Stages completed: {len([r for r in result.stage_results if r.status.value == 'completed'])}/3")

        if result.product_description:
            print("\n📝 Generated Product Description:")
            print(f"Title: {result.product_description.title}")
            print(f"Short Description: {result.product_description.short_description[:100]}...")
            print(f"Key Features: {', '.join(result.product_description.key_features[:3])}")

        if result.generated_image:
            print("\n🖼️ Generated Image:")
            print(f"URL: {result.generated_image.image_url}")
            print(f"Quality Score: {result.generated_image.quality_score}")

        if result.shopify_listing:
            print("\n🛒 Shopify Listing:")
            print(f"Handle: {result.shopify_listing.handle}")
            print(f"SEO Title: {result.shopify_listing.seo_title}")
            print(f"Tags: {', '.join(result.shopify_listing.tags[:5])}")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

    finally:
        await orchestrator.shutdown()

# Example 2: Web scraping from URL
async def example_url_scraping():
    """
    Example: Create product listing by scraping from a URL.
    """

    print("\n🌐 Example 2: Web Scraping to Product Listing")
    print("=" * 50)

    from ..config.configuration import load_default_configuration
    from ..orchestrator import ProductListingOrchestrator
    from ..models.data_models import ProductInput

    # Load configuration
    config = load_default_configuration()
    orchestrator = ProductListingOrchestrator(config)

    # Create product input with URL (using a hypothetical product URL)
    product_input = ProductInput(
        product_url="https://example-store.com/products/smart-watch",
        additional_context="Focus on fitness and health tracking features"
    )

    try:
        print("⏳ Scraping product data and generating listing...")
        result = await orchestrator.execute_pipeline(product_input)

        print(f"✅ Pipeline Status: {result.final_status.value}")

        # Show stage-by-stage results
        for stage_result in result.stage_results:
            status_emoji = "✅" if stage_result.status.value == "completed" else "❌"
            print(f"{status_emoji} Stage {stage_result.stage} ({stage_result.agent_type.value}): {stage_result.status.value}")

            if stage_result.error_message:
                print(f"   Error: {stage_result.error_message}")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

    finally:
        await orchestrator.shutdown()

# Example 3: High-level API usage
async def example_high_level_api():
    """
    Example: Using the high-level API wrapper.
    """

    print("\n🎯 Example 3: High-Level API Usage")
    print("=" * 50)

    from ..config.configuration import load_default_configuration
    from ..orchestrator import ProductListingAPI

    # Load configuration
    config = load_default_configuration()
    api = ProductListingAPI(config)

    try:
        # Create listing from description
        print("⏳ Creating listing using high-level API...")

        result = await api.create_listing_from_description(
            title="Eco-Friendly Bamboo Phone Case",
            description="Sustainable phone case made from bamboo fiber. Lightweight, durable, and environmentally conscious.",
            brand="EcoTech",
            price=24.99
        )

        print(f"✅ Success: {result['success']}")
        print(f"⏱️ Execution Time: {result['execution_time']:.2f}s")
        print(f"📊 Stages Completed: {result['stages_completed']}/{result['total_stages']}")

        if result['success'] and 'shopify_listing' in result:
            listing = result['shopify_listing']
            print(f"🛒 Shopify Ready: {listing['title']}")
            print(f"🔗 Handle: {listing['handle']}")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

# Example 4: Health monitoring
async def example_health_monitoring():
    """
    Example: System health monitoring and status checking.
    """

    print("\n🏥 Example 4: System Health Monitoring")
    print("=" * 50)

    from ..config.configuration import load_default_configuration
    from ..orchestrator import ProductListingOrchestrator

    config = load_default_configuration()
    orchestrator = ProductListingOrchestrator(config)

    try:
        # Get health status
        health_status = orchestrator.get_health_status()

        print("🎯 Orchestrator Status:")
        orch_status = health_status['orchestrator']
        print(f"  Status: {orch_status['status']}")
        print(f"  Active Pipelines: {orch_status['active_pipelines']}")
        print(f"  Agents Initialized: {orch_status['agents_initialized']}")

        print("\n🤖 Agent Status:")
        for agent_name, agent_health in health_status['agents'].items():
            status_emoji = "✅" if agent_health.get('status') != 'error' else "❌"
            print(f"  {status_emoji} {agent_name}: {agent_health.get('enabled', 'unknown')}")
            if 'error' in agent_health:
                print(f"     Error: {agent_health['error']}")

        return health_status

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

    finally:
        await orchestrator.shutdown()

# Example 5: Error handling and recovery
async def example_error_handling():
    """
    Example: Demonstrating error handling and recovery mechanisms.
    """

    print("\n🛠️ Example 5: Error Handling and Recovery")
    print("=" * 50)

    from ..config.configuration import load_default_configuration
    from ..orchestrator import ProductListingOrchestrator
    from ..models.data_models import ProductInput

    config = load_default_configuration()
    orchestrator = ProductListingOrchestrator(config)

    # Create input that might cause issues
    problematic_input = ProductInput(
        product_url="https://invalid-url-that-does-not-exist.com/product",
        product_title="Test Product"  # Fallback data
    )

    try:
        print("⏳ Testing error handling with problematic input...")
        result = await orchestrator.execute_pipeline(problematic_input)

        print(f"📊 Final Status: {result.final_status.value}")

        if result.error_summary:
            print("\n⚠️ Errors Encountered:")
            for error in result.error_summary:
                print(f"  • {error}")

        print("\n📋 Stage Details:")
        for stage_result in result.stage_results:
            if stage_result.status.value == "failed":
                print(f"❌ Stage {stage_result.stage}: {stage_result.error_message}")
            elif stage_result.status.value == "completed":
                print(f"✅ Stage {stage_result.stage}: Success (recovered)")
            else:
                print(f"⏭️ Stage {stage_result.stage}: {stage_result.status.value}")

        return result

    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return None

    finally:
        await orchestrator.shutdown()

# Test runner
async def run_all_examples():
    """Run all example scenarios."""

    print("🎯 Multi-Agent Product Listing System Examples")
    print("=" * 60)

    examples = [
        ("Basic Description", example_basic_description),
        ("URL Scraping", example_url_scraping),
        ("High-Level API", example_high_level_api),
        ("Health Monitoring", example_health_monitoring),
        ("Error Handling", example_error_handling)
    ]

    results = {}

    for name, example_func in examples:
        try:
            print(f"\n▶️ Running: {name}")
            result = await example_func()
            results[name] = {"success": True, "result": result}
        except Exception as e:
            print(f"❌ Example '{name}' failed: {str(e)}")
            results[name] = {"success": False, "error": str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("📊 EXAMPLES SUMMARY")
    print("=" * 60)

    for name, result in results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{status} {name}")
        if not result["success"]:
            print(f"   Error: {result['error']}")

    success_count = sum(1 for r in results.values() if r["success"])
    print(f"\n🎯 Results: {success_count}/{len(examples)} examples passed")

# Utility functions for testing
def create_test_product_input() -> 'ProductInput':
    """Create a test product input for demonstrations."""
    from ..models.data_models import ProductInput

    return ProductInput(
        product_title="Professional Gaming Mechanical Keyboard",
        product_description="RGB backlit mechanical keyboard with tactile switches, programmable keys, and premium build quality.",
        brand="GameTech Pro",
        price=149.99,
        product_category="Gaming Accessories"
    )

def save_example_results(results: Dict[str, Any], filename: str = "example_results.json"):
    """Save example results to a JSON file for analysis."""

    # Convert datetime objects to strings for JSON serialization
    def serialize_datetime(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError(f"Object {obj} is not JSON serializable")

    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=serialize_datetime)
        print(f"📁 Results saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save results: {str(e)}")

if __name__ == "__main__":
    # Run examples if script is executed directly
    asyncio.run(run_all_examples())
