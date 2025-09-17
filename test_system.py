#!/usr/bin/env python3
"""
Simple test script for the Multi-Agent Product Listing System
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import directly from modules
    from orchestrator import ProductListingOrchestrator
    from config.configuration import initialize_config
    print("✅ Import successful!")

    # Initialize configuration
    config = initialize_config()
    print("✅ Configuration loaded!")

    # Create orchestrator
    orchestrator = ProductListingOrchestrator(config)
    print("✅ Orchestrator created!")

    print("\n🎉 System is ready to test!")
    print("You can now create product listings using the orchestrator.")
    print("\nExample usage:")
    print("result = await orchestrator.process_product_listing(")
    print("    product_description='Eco-friendly water bottle'")
    print(")")
    print("print(result.to_xml())")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Make sure you're running this from the project root directory.")
except Exception as e:
    print(f"❌ Error: {e}")
