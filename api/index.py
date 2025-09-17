from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import asyncio

# Initialize FastAPI
app = FastAPI(title="Multi-Agent Product Listing System")

# Setup templates
templates = Path(__file__).parent.parent / "templates"
templates.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates))

@app.get("/")
async def home():
    """Serve the main demo page"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Product Listing System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .demo-notice {
            background: #e3f2fd; border: 1px solid #2196f3; color: #1976d2;
            padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center;
        }
        .demo-section {
            background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .generate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 15px 30px; border-radius: 8px;
            font-size: 18px; font-weight: 600; cursor: pointer; width: 100%;
        }
        .result { display: none; margin-top: 30px; }
        .result-section {
            background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;
        }
        .result-content {
            background: white; border: 1px solid #e1e5e9; border-radius: 4px;
            padding: 15px; font-family: monospace; max-height: 300px; overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Multi-Agent Product Listing System</h1>
            <p>Generate complete product listings with AI-powered descriptions and images</p>
        </div>

        <div class="demo-notice">
            <strong>🚀 Deployed on Vercel:</strong> This is the live demo running on Vercel serverless functions.
        </div>

        <div class="demo-section">
            <h2 style="margin-bottom: 20px; color: #333;">🎨 Generate Product Listing</h2>

            <form id="productForm">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Product Description *</label>
                    <textarea id="description" name="product_description" placeholder="Describe your product..." required style="width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; min-height: 100px;"></textarea>
                </div>

                <button type="submit" class="generate-btn" id="generateBtn">🚀 Generate Listing</button>
            </form>

            <div id="loading" style="display: none; text-align: center; margin-top: 20px;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px;"></div>
                <p>AI is working its magic... (Demo: 2 seconds)</p>
            </div>

            <div class="result" id="result">
                <h3 style="margin-bottom: 20px; color: #333;">✅ Your Product Listing is Ready!</h3>

                <div class="result-section">
                    <div style="font-size: 1.2em; font-weight: 600; margin-bottom: 10px;">📝 Enhanced Title</div>
                    <div class="result-content" id="resultTitle"></div>
                </div>

                <div class="result-section">
                    <div style="font-size: 1.2em; font-weight: 600; margin-bottom: 10px;">📖 Enhanced Description</div>
                    <div class="result-content" id="resultDescription"></div>
                </div>

                <div class="result-section">
                    <div style="font-size: 1.2em; font-weight: 600; margin-bottom: 10px;">📄 Shopify-Ready XML</div>
                    <div class="result-content" id="resultXML"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('productForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const generateBtn = document.getElementById('generateBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');

            generateBtn.disabled = true;
            generateBtn.textContent = 'Generating...';
            loading.style.display = 'block';
            result.style.display = 'none';

            try {
                const response = await fetch('/api/generate', { method: 'POST', body: new FormData(this) });
                const data = await response.json();

                document.getElementById('resultTitle').textContent = data.title;
                document.getElementById('resultDescription').textContent = data.description;
                document.getElementById('resultXML').textContent = data.xml_output;
                result.style.display = 'block';
            } catch (err) {
                console.error('Error:', err);
            } finally {
                generateBtn.disabled = false;
                generateBtn.textContent = '🚀 Generate Listing';
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>
""")

@app.post("/generate")
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
    import random
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
