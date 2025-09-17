# Multi-Agent Product Listing System

A comprehensive automated system for creating product listings using specialized AI agents with **Replicate nano-banana** integration for high-quality image generation.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for each workflow stage
- **Replicate Integration**: Advanced image generation using Google's nano-banana model
- **Web Scraping**: Extract product details from URLs
- **AI Enhancement**: Improve product descriptions with OpenAI
- **Shopify Ready**: Direct e-commerce platform integration
- **Type Safe**: Full Pydantic validation and type hints
- **Production Ready**: Comprehensive error handling and logging
- **Async Support**: Non-blocking operations for better performance

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Description   │    │     Image       │    │   E-commerce    │
│     Agent       │───►│   Generation    │───►│     Agent       │
│                 │    │     Agent       │    │                 │
│ • Web scraping  │    │ • Replicate API │    │ • Shopify API   │
│ • AI enhancement│    │ • nano-banana   │    │ • Product format│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 Installation

### Quick Start

1. **Clone or extract the package**
   ```bash
   tar -xzf multi-agent-product-system.tar.gz
   cd multi_agent_product_system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   ```bash
   cp .env.sample .env
   # Edit .env with your API keys (see Configuration section)
   ```

4. **Install the package**
   ```bash
   pip install -e .
   ```

## ⚙️ Configuration

### Required API Keys

1. **Replicate API Token** (Required for image generation)
   - Get token: https://replicate.com/account/api-tokens
   - Set in `.env`: `REPLICATE_API_TOKEN=r8_your_token_here`

2. **OpenAI API Key** (Optional, for description enhancement)
   - Get key: https://platform.openai.com/api-keys
   - Set in `.env`: `OPENAI_API_KEY=sk-your_key_here`

3. **Shopify Credentials** (Optional, for e-commerce integration)
   - API Key, Secret, and Store URL
   - Set in `.env` file

### Environment Configuration

```bash
# .env file example
REPLICATE_API_TOKEN=r8_your_replicate_token_here
OPENAI_API_KEY=sk-your_openai_key_here

# Image Generation Settings (Replicate nano-banana)
IMAGE_WIDTH=1024
IMAGE_HEIGHT=1024
IMAGE_STEPS=20
IMAGE_GUIDANCE=7.5

# Shopify Integration (optional)
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_SECRET=your_shopify_secret
SHOPIFY_STORE_URL=your-store.myshopify.com
```

## 🚀 How to Use

This comprehensive guide will walk you through using the Multi-Agent Product Listing System from installation to creating your first automated product listing.

### Prerequisites

Before getting started, ensure you have:

- **Python 3.8+** installed on your system
- **Poetry** for dependency management (`pip install poetry`)
- **API Keys** for the services you want to use:
  - **Replicate API Token** (required for image generation)
  - **OpenAI API Key** (optional, for description enhancement)
  - **Shopify Credentials** (optional, for e-commerce integration)

### Step 1: Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd multi-agent-product-system
   ```

2. **Install dependencies with Poetry:**
   ```bash
   poetry install
   ```

3. **Activate the Poetry environment:**
   ```bash
   poetry shell
   ```

### Step 2: Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.sample .env
   ```

2. **Edit `.env` with your API keys:**
   ```bash
   # Required: Replicate API for image generation
   REPLICATE_API_TOKEN=r8_your_replicate_token_here

   # Optional: OpenAI for description enhancement
   OPENAI_API_KEY=sk-your_openai_key_here

   # Optional: Shopify for e-commerce integration
   SHOPIFY_API_KEY=your_shopify_api_key_here
   SHOPIFY_SECRET=your_shopify_secret_here
   SHOPIFY_STORE_URL=your-store.myshopify.com
   ```

3. **Get your API keys:**
   - **Replicate**: Visit [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)
   - **OpenAI**: Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - **Shopify**: Follow the guide in your terminal output

### Step 3: Your First Product Listing

Create a new Python file (e.g., `create_listing.py`):

```python
#!/usr/bin/env python3
"""
Create your first automated product listing
"""

import asyncio
from multi_agent_product_system import ProductListingOrchestrator
from multi_agent_product_system.config.configuration import initialize_config

async def create_first_listing():
    """Generate a product listing from a simple description"""

    # Step 1: Load configuration (reads your .env file)
    print("🔧 Loading configuration...")
    config = initialize_config()

    # Step 2: Create the orchestrator
    print("🤖 Initializing AI agents...")
    orchestrator = ProductListingOrchestrator(config)

    # Step 3: Generate your product listing
    print("🎨 Creating product listing...")
    result = await orchestrator.process_product_listing(
        product_description="Eco-friendly bamboo water bottle with thermal insulation"
    )

    # Step 4: Display results
    print("\n" + "="*60)
    print("✅ PRODUCT LISTING GENERATED!")
    print("="*60)

    print(f"📝 Enhanced Description: {result.product_description.enhanced_description[:100]}...")
    print(f"🖼️  Generated Image: {result.product_image.url}")
    print(f"🏪 Shopify Ready: {result.shopify_ready}")

    # Step 5: Get the complete XML output
    xml_output = result.to_xml()
    print(f"\n📄 Complete XML Output:\n{xml_output}")

    return result

# Run the async function
if __name__ == "__main__":
    asyncio.run(create_first_listing())
```

Run it:
```bash
python create_listing.py
```

### Step 4: Understanding the Output

The system returns a structured result with:

```python
result.product_description  # Enhanced marketing copy
result.product_image       # Generated image details
result.shopify_listing     # Shopify-formatted data
result.to_xml()           # Complete XML output
```

**Sample Output:**
```xml
<product_listing>
  <title>Eco-Friendly Bamboo Water Bottle with Thermal Insulation</title>
  <description>Stay hydrated sustainably with our premium bamboo water bottle. Crafted from renewable bamboo with advanced thermal insulation technology...</description>
  <image_url>https://replicate.delivery/generated-image-url</image_url>
  <shopify_ready>true</shopify_ready>
  <seo_title>Eco-Friendly Bamboo Water Bottle | Thermal Insulated</seo_title>
  <tags>eco-friendly,bamboo,water-bottle,thermal,insulated,sustainable</tags>
</product_listing>
```

### Step 5: Advanced Usage Examples

#### A. Custom Image Generation
```python
# Customize image generation parameters
image_params = {
    "width": 1024,        # Image width (512-2048)
    "height": 1024,       # Image height (512-2048)
    "steps": 30,          # Quality steps (1-100, higher = better quality)
    "guidance": 8.0,      # Prompt adherence (0-20, higher = more precise)
    "seed": 42            # Reproducibility (optional)
}

result = await orchestrator.process_product_listing(
    product_description="Vintage leather messenger bag",
    image_generation_params=image_params
)
```

#### B. Full Product Input
```python
from multi_agent_product_system.models.data_models import ProductInput

# Create detailed product information
product = ProductInput(
    product_title="Premium Wireless Headphones",
    product_description="High-quality wireless headphones with noise cancellation, 30-hour battery life",
    brand="AudioTech",
    price=199.99,
    product_category="Electronics",
    target_audience="Music lovers and professionals"
)

result = await orchestrator.process_product_listing(product_input=product)
```

#### C. Web Scraping from URL
```python
# Generate listing by scraping product data from a website
result = await orchestrator.process_product_listing(
    product_url="https://example-store.com/products/headphones",
    additional_context="Focus on sound quality and comfort features"
)
```

#### D. Batch Processing
```python
# Process multiple products
products = [
    "Organic cotton t-shirt with minimalist design",
    "Smart fitness tracker with heart rate monitor",
    "Wireless charging pad with fast charging"
]

for description in products:
    result = await orchestrator.process_product_listing(
        product_description=description
    )
    print(f"✅ Generated: {result.product_description.title}")
```

### Step 6: Integration Examples

#### Save to File
```python
# Save the XML output to a file
with open('product_listing.xml', 'w') as f:
    f.write(result.to_xml())

print("💾 Saved to product_listing.xml")
```

#### Use in Web Application
```python
# Example FastAPI integration
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ProductRequest(BaseModel):
    description: str
    title: str = None
    brand: str = None

@app.post("/generate-listing")
async def generate_listing(request: ProductRequest):
    try:
        config = initialize_config()
        orchestrator = ProductListingOrchestrator(config)

        result = await orchestrator.process_product_listing(
            product_description=request.description
        )

        return {
            "success": True,
            "title": result.product_description.title,
            "description": result.product_description.enhanced_description,
            "image_url": result.product_image.url,
            "xml_output": result.to_xml()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 7: Troubleshooting

#### Common Issues:

**❌ "Module not found" errors:**
```bash
# Make sure you're in the Poetry environment
poetry shell

# Or run with poetry run
poetry run python your_script.py
```

**❌ API key errors:**
- Check your `.env` file has the correct keys
- Ensure API keys have sufficient credits
- Verify keys are not expired

**❌ Image generation fails:**
- Check your Replicate API token
- Ensure you have credits in your Replicate account
- Try with simpler prompts first

**❌ Slow processing:**
- Image generation takes 10-30 seconds
- OpenAI enhancement adds 5-15 seconds
- Total time: 30-60 seconds per product

#### Debug Mode:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
result = await orchestrator.process_product_listing(
    product_description="Test product",
    debug=True
)
```

### Step 8: Production Deployment

#### Docker Deployment:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .
RUN poetry install --no-dev

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "your_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Variables for Production:
```bash
REPLICATE_API_TOKEN=r8_your_token
OPENAI_API_KEY=sk-your_key
SHOPIFY_API_KEY=your_key
SHOPIFY_SECRET=your_secret
SHOPIFY_STORE_URL=your-store.myshopify.com

# Production settings
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=300
ENVIRONMENT=production
```

### Next Steps

🎉 **Congratulations!** You've successfully set up and used the Multi-Agent Product Listing System. Here are some next steps:

1. **Experiment** with different product types and descriptions
2. **Customize** image generation parameters for your brand
3. **Integrate** the system into your existing workflow
4. **Batch process** multiple products for efficiency
5. **Deploy** to production for automated listing generation

### Need Help?

- 📖 Check the [API Reference](config/configuration.py) for detailed parameters
- 🐛 Report issues on GitHub
- 💬 Check existing issues for common solutions
- 📧 Contact support for enterprise assistance

**Happy automating! 🚀**

## 📚 Documentation

- **Configuration Guide**: See `config/configuration.py` for all settings
- **Usage Examples**: Check `examples/replicate_usage_examples.py`
- **API Reference**: Each agent has comprehensive docstrings
- **Error Handling**: Built-in retry logic and graceful degradation

## 🔧 Replicate nano-banana Model

This system uses Google's nano-banana model via Replicate for image generation:

- **Model**: `google/nano-banana`
- **Quality**: High-resolution product images
- **Speed**: Fast generation times (~10-20 seconds)
- **Cost**: Approximately $0.00025 per image
- **Parameters**: Customizable width, height, steps, guidance, and seed

### Supported Parameters

```python
{
    "width": 512-2048,        # Image width
    "height": 512-2048,       # Image height  
    "num_inference_steps": 1-100,  # Quality vs speed
    "guidance_scale": 0-20,   # Prompt adherence
    "seed": -1 or int        # Reproducibility
}
```

## 🎯 Agent Details

### Description Agent
- Web scraping with BeautifulSoup
- AI-powered description enhancement
- Product detail extraction
- SEO optimization

### Image Generation Agent  
- Replicate nano-banana integration
- Custom parameter support
- Image quality validation
- Cost estimation

### E-commerce Agent
- Shopify API integration
- Product listing formatting
- Inventory management
- SEO metadata

## 🚢 Deployment

### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# REPLICATE_API_TOKEN, OPENAI_API_KEY, etc.
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📋 Requirements

- Python 3.8+
- Replicate API access
- OpenAI API (optional)
- Shopify store (optional)

## 🛠️ Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black .
isort .

# Type checking
mypy .
```

## 📈 Performance

- **Processing Time**: 30-60 seconds per product
- **Image Generation**: 10-20 seconds (Replicate nano-banana)
- **Concurrent Processing**: Supported with async/await
- **Error Recovery**: Automatic retry with exponential backoff

## 🔒 Security

- API key validation and masking
- Input sanitization for web scraping
- Secure environment variable handling
- Rate limiting for external APIs

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: Check docstrings and examples
- **Replicate Help**: https://replicate.com/docs
- **API Keys**: Ensure tokens are valid and have sufficient credits

---

**Ready to automate your product listings with AI-powered agents and Replicate's nano-banana model!** 🚀
