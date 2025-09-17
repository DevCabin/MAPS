#!/usr/bin/env python3
"""
Simple web demo for the Multi-Agent Product Listing System
This version works without complex imports - just shows the interface
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import asyncio
import time

# Initialize FastAPI
app = FastAPI(title="Multi-Agent Product Listing Demo")

# Setup templates
templates = Path(__file__).parent / "templates"
templates.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main demo page"""
    return templates.TemplateResponse("simple_demo.html", {"request": request})

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

# Create the HTML template
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Product Listing Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .demo-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }

        textarea, input[type="text"], input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        textarea:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        .advanced-options {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }

        .advanced-toggle {
            background: none;
            border: none;
            color: #667eea;
            cursor: pointer;
            font-weight: 600;
            text-decoration: underline;
        }

        .options-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .generate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }

        .generate-btn:hover {
            transform: translateY(-2px);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .result {
            display: none;
            margin-top: 30px;
        }

        .result-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .result-title {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }

        .result-content {
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 4px;
            padding: 15px;
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 300px;
            overflow-y: auto;
        }

        .image-preview {
            text-align: center;
            margin: 20px 0;
        }

        .image-preview img {
            max-width: 100%;
            max-height: 400px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .error {
            background: #fee;
            border: 1px solid #fcc;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }

        .instructions {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .instructions h2 {
            color: #333;
            margin-bottom: 20px;
        }

        .instruction-step {
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .step-number {
            display: inline-block;
            background: #667eea;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-weight: bold;
            margin-right: 10px;
        }

        .code-snippet {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            margin: 10px 0;
            overflow-x: auto;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .feature-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .feature-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .feature-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }

        .demo-notice {
            background: #e3f2fd;
            border: 1px solid #2196f3;
            color: #1976d2;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            .header h1 {
                font-size: 2em;
            }

            .options-grid {
                grid-template-columns: 1fr;
            }

            .feature-grid {
                grid-template-columns: 1fr;
            }
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
            <strong>🎭 Demo Mode:</strong> This shows mock responses. To use real AI, set up API keys and run the full system.
        </div>

        <div class="instructions">
            <h2>🚀 How to Use This Demo</h2>

            <div class="instruction-step">
                <span class="step-number">1</span>
                <strong>Enter a product description</strong> in the text area below. Be as descriptive as you like!
                <div class="code-snippet">Example: "Eco-friendly bamboo water bottle with thermal insulation, 500ml capacity, perfect for hiking and daily use"</div>
            </div>

            <div class="instruction-step">
                <span class="step-number">2</span>
                <strong>Customize image settings</strong> (optional) - adjust width, height, quality, and style guidance.
            </div>

            <div class="instruction-step">
                <span class="step-number">3</span>
                <strong>Click "Generate Listing"</strong> and see instant mock results.
            </div>

            <div class="instruction-step">
                <span class="step-number">4</span>
                <strong>View your results</strong> - enhanced description, sample image, and Shopify-ready XML.
            </div>
        </div>

        <div class="demo-section">
            <h2 style="margin-bottom: 20px; color: #333;">🎨 Generate Product Listing</h2>

            <form id="productForm">
                <div class="form-group">
                    <label for="description">Product Description *</label>
                    <textarea
                        id="description"
                        name="product_description"
                        placeholder="Describe your product in detail..."
                        required
                    >Eco-friendly bamboo water bottle with thermal insulation, 500ml capacity, perfect for hiking and daily use</textarea>
                </div>

                <button type="button" class="advanced-toggle" onclick="toggleAdvanced()">
                    ⚙️ Advanced Image Options
                </button>

                <div class="advanced-options" id="advancedOptions" style="display: none;">
                    <div class="options-grid">
                        <div class="form-group">
                            <label for="width">Image Width (512-2048)</label>
                            <input type="number" id="width" name="custom_width" value="1024" min="512" max="2048">
                        </div>
                        <div class="form-group">
                            <label for="height">Image Height (512-2048)</label>
                            <input type="number" id="height" name="custom_height" value="1024" min="512" max="2048">
                        </div>
                        <div class="form-group">
                            <label for="steps">Quality Steps (1-100)</label>
                            <input type="number" id="steps" name="custom_steps" value="20" min="1" max="100">
                        </div>
                        <div class="form-group">
                            <label for="guidance">Style Guidance (0-20)</label>
                            <input type="number" id="guidance" name="custom_guidance" value="7.5" min="0" max="20" step="0.1">
                        </div>
                    </div>
                </div>

                <button type="submit" class="generate-btn" id="generateBtn">
                    🚀 Generate Listing
                </button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>AI is working its magic... (Demo: 2 seconds)</p>
            </div>

            <div class="result" id="result">
                <h3 style="margin-bottom: 20px; color: #333;">✅ Your Product Listing is Ready!</h3>

                <div class="result-section">
                    <div class="result-title">📝 Enhanced Title</div>
                    <div class="result-content" id="resultTitle"></div>
                </div>

                <div class="result-section">
                    <div class="result-title">📖 Enhanced Description</div>
                    <div class="result-content" id="resultDescription"></div>
                </div>

                <div class="image-preview">
                    <div class="result-title">🖼️ Generated Product Image</div>
                    <img id="resultImage" src="" alt="Generated product image" style="display: none;">
                    <p id="imageLoading">Generating image...</p>
                </div>

                <div class="result-section">
                    <div class="result-title">📄 Shopify-Ready XML</div>
                    <div class="result-content" id="resultXML"></div>
                </div>
            </div>

            <div class="error" id="error" style="display: none;"></div>
        </div>

        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <div class="feature-title">AI Image Generation</div>
                <p>Uses Google's nano-banana model via Replicate for high-quality product images</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">✍️</div>
                <div class="feature-title">Smart Descriptions</div>
                <p>OpenAI-powered enhancement creates marketing-ready product descriptions</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">🏪</div>
                <div class="feature-title">Shopify Ready</div>
                <p>Automatically formats listings for direct import into Shopify stores</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Fast Processing</div>
                <p>Complete listings generated in 30-60 seconds with async processing</p>
            </div>
        </div>
    </div>

    <script>
        let advancedVisible = false;

        function toggleAdvanced() {
            advancedVisible = !advancedVisible;
            const options = document.getElementById('advancedOptions');
            const toggle = document.querySelector('.advanced-toggle');

            if (advancedVisible) {
                options.style.display = 'block';
                toggle.textContent = '⚙️ Hide Advanced Options';
            } else {
                options.style.display = 'none';
                toggle.textContent = '⚙️ Advanced Image Options';
            }
        }

        document.getElementById('productForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const generateBtn = document.getElementById('generateBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const error = document.getElementById('error');

            // Show loading
            generateBtn.disabled = true;
            generateBtn.textContent = 'Generating...';
            loading.style.display = 'block';
            result.style.display = 'none';
            error.style.display = 'none';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Show results
                    document.getElementById('resultTitle').textContent = data.title;
                    document.getElementById('resultDescription').textContent = data.description;

                    // Handle image
                    const imageElement = document.getElementById('resultImage');
                    const imageLoading = document.getElementById('imageLoading');

                    if (data.image_url) {
                        imageElement.src = data.image_url;
                        imageElement.style.display = 'block';
                        imageLoading.style.display = 'none';
                    } else {
                        imageLoading.textContent = 'Image generation failed';
                    }

                    document.getElementById('resultXML').textContent = data.xml_output;
                    result.style.display = 'block';
                } else {
                    throw new Error(data.error || 'Unknown error occurred');
                }

            } catch (err) {
                error.textContent = `❌ Error: ${err.message}`;
                error.style.display = 'block';
            } finally {
                // Reset UI
                generateBtn.disabled = false;
                generateBtn.textContent = '🚀 Generate Listing';
                loading.style.display = 'none';
            }
        });

        // Load some example descriptions
        const examples = [
            "Eco-friendly bamboo water bottle with thermal insulation, 500ml capacity, perfect for hiking and daily use",
            "Premium wireless Bluetooth headphones with noise cancellation, 30-hour battery life, comfortable over-ear design",
            "Organic cotton t-shirt with minimalist design, available in multiple colors, sustainable and comfortable",
            "Smart fitness tracker with heart rate monitor, GPS, and 7-day battery life for serious athletes"
        ];

        // Add example buttons
        const descriptionTextarea = document.getElementById('description');
        const examplesHtml = examples.map((example, index) =>
            `<button type="button" onclick="descriptionTextarea.value = '${example.replace(/'/g, "\\'")}'" style="margin: 5px; padding: 5px 10px; background: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; cursor: pointer;">Example ${index + 1}</button>`
        ).join('');

        descriptionTextarea.insertAdjacentHTML('afterend', '<div style="margin-top: 10px;">Try these examples: ' + examplesHtml + '</div>');
    </script>
</body>
</html>
"""

# Write the HTML template
with open(templates / "simple_demo.html", "w") as f:
    f.write(html_content)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Multi-Agent Product Listing Demo (Simple Mode)...")
    print("📱 Visit: http://localhost:8000")
    print("❌ To stop: Ctrl+C")
    print()
    print("🎭 Note: This is demo mode with mock responses.")
    print("   To use real AI, set up API keys and run the full system.")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
