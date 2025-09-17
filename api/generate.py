import json
import random

def handler(request):
    """Vercel serverless function handler for product generation"""

    # Mock response data
    mock_responses = [
        {
            "success": True,
            "title": "Eco-Friendly Bamboo Water Bottle with Thermal Insulation",
            "description": "Stay hydrated sustainably with our premium bamboo water bottle. Crafted from renewable bamboo with advanced thermal insulation technology that keeps drinks cold for 24 hours or hot for 12 hours. Features a leak-proof cap, wide mouth for easy cleaning, and comfortable carry strap. Perfect for hiking, office, gym, or daily use. 500ml capacity, BPA-free, and environmentally conscious.",
            "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop",
            "shopify_ready": True,
            "xml_output": "<product>\n  <title>Eco-Friendly Bamboo Water Bottle with Thermal Insulation</title>\n  <description>Stay hydrated sustainably with our premium bamboo water bottle...</description>\n  <image>https://images.unsplash.com/photo-1602143407151-7111542de6e8</image>\n  <price>29.99</price>\n  <tags>eco-friendly,bamboo,water-bottle,thermal,insulated,sustainable</tags>\n</product>",
            "processing_time": "2.1 seconds",
            "note": "This is a demo response. Set up API keys for real AI generation."
        },
        {
            "success": True,
            "title": "Premium Wireless Bluetooth Headphones",
            "description": "Experience superior sound quality with our premium wireless Bluetooth headphones. Featuring active noise cancellation, 30-hour battery life, and comfortable over-ear design. Includes touch controls, voice assistant compatibility, and premium drivers for rich, immersive audio. Perfect for music lovers, commuters, and professionals.",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
            "shopify_ready": True,
            "xml_output": "<product>\n  <title>Premium Wireless Bluetooth Headphones</title>\n  <description>Experience superior sound quality with our premium wireless...</description>\n  <image>https://images.unsplash.com/photo-1505740420928-5e560c06d30e</image>\n  <price>199.99</price>\n  <tags>wireless,bluetooth,headphones,noise-cancellation,premium</tags>\n</product>",
            "processing_time": "2.1 seconds",
            "note": "This is a demo response. Set up API keys for real AI generation."
        }
    ]

    # Return a random mock response
    response = random.choice(mock_responses)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(response)
    }
