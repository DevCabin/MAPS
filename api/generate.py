from fastapi import Form
import asyncio
import random

async def generate_listing(
    product_description: str = Form(...),
    custom_width: int = Form(1024),
    custom_height: int = Form(1024),
    custom_steps: int = Form(20),
    custom_guidance: float = Form(7.5)
):
    """Mock generate a product listing"""
    # Simulate processing time
    await asyncio.sleep(2)

    # Mock response data
    mock_responses = [
        {
            "title": "Eco-Friendly Bamboo Water Bottle with Thermal Insulation",
            "description": "Stay hydrated sustainably with our premium bamboo water bottle. Crafted from renewable bamboo with advanced thermal insulation technology that keeps drinks cold for 24 hours or hot for 12 hours. Features a leak-proof cap, wide mouth for easy cleaning, and comfortable carry strap. Perfect for hiking, office, gym, or daily use. 500ml capacity, BPA-free, and environmentally conscious.",
            "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop",
            "xml_output": """<product>
  <title>Eco-Friendly Bamboo Water Bottle with Thermal Insulation</title>
  <description>Stay hydrated sustainably with our premium bamboo water bottle...</description>
  <image>https://images.unsplash.com/photo-1602143407151-7111542de6e8</image>
  <price>29.99</price>
  <tags>eco-friendly,bamboo,water-bottle,thermal,insulated,sustainable</tags>
</product>"""
        },
        {
            "title": "Premium Wireless Bluetooth Headphones",
            "description": "Experience superior sound quality with our premium wireless Bluetooth headphones. Featuring active noise cancellation, 30-hour battery life, and comfortable over-ear design. Includes touch controls, voice assistant compatibility, and premium drivers for rich, immersive audio. Perfect for music lovers, commuters, and professionals.",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
            "xml_output": """<product>
  <title>Premium Wireless Bluetooth Headphones</title>
  <description>Experience superior sound quality with our premium wireless...</description>
  <image>https://images.unsplash.com/photo-1505740420928-5e560c06d30e</image>
  <price>199.99</price>
  <tags>wireless,bluetooth,headphones,noise-cancellation,premium</tags>
</product>"""
        }
    ]

    # Return a mock response
    response = random.choice(mock_responses)

    return {
        "success": True,
        "title": response["title"],
        "description": response["description"],
        "image_url": response["image_url"],
        "shopify_ready": True,
        "xml_output": response["xml_output"],
        "processing_time": "2.1 seconds",
        "note": "This is a demo response. Set up API keys for real AI generation."
    }
