# Multi-Agent Product Listing System - Web Demo

A beautiful, interactive web interface for testing the Multi-Agent Product Listing System.

## 🚀 Quick Start

### Option 1: Auto-Magic Script (Easiest)
```bash
# Make executable and run - handles everything automatically
chmod +x run_demo.sh
./run_demo.sh
```

### Option 2: Manual Python Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the web demo
python simple_web_demo.py
```

### Option 3: Static HTML Demo (No Python Required)
```bash
# Just open this file in your browser
open static_demo.html
# Or double-click the file
```

### Option 4: Using Poetry (Advanced)
```bash
# Install dependencies
poetry install

# Run the web demo
poetry run python web_demo.py
```

## 📱 Using the Web Demo

1. **Open your browser** and go to: `http://localhost:8000`

2. **Enter a product description** in the text area (e.g., "Eco-friendly bamboo water bottle with thermal insulation")

3. **Customize image settings** (optional):
   - **Width/Height**: Image dimensions (512-2048px)
   - **Quality Steps**: Higher = better quality but slower (1-100)
   - **Style Guidance**: How closely to follow your description (0-20)

4. **Click "Generate Listing"** and wait 30-60 seconds

5. **View your results**:
   - Enhanced product title and description
   - AI-generated product image
   - Complete Shopify-ready XML

## 🎨 Features

### ✨ Interactive Interface
- **Step-by-step instructions** built into the page
- **Example product descriptions** with one-click loading
- **Advanced options** toggle for image customization
- **Real-time feedback** during generation

### 🤖 AI-Powered Generation
- **Google nano-banana** for high-quality product images
- **OpenAI GPT** for marketing copy enhancement
- **Shopify formatting** for direct e-commerce integration

### 🎯 What It Demonstrates
- Complete product listing workflow
- Customizable image generation parameters
- Error handling and user feedback
- Production-ready output formatting

## 🔧 Technical Details

### Backend
- **FastAPI** web framework
- **Jinja2** templating
- **Uvicorn** ASGI server
- **Async/await** for concurrent processing

### Frontend
- **Vanilla JavaScript** (no frameworks needed)
- **Responsive design** works on mobile/desktop
- **Modern CSS** with gradients and animations
- **Form validation** and error handling

### API Integration
- **Replicate API** for image generation
- **OpenAI API** for text enhancement
- **Environment variables** for secure configuration

## 📋 Requirements

- **Python 3.8+**
- **API Keys** configured in `.env`:
  - `REPLICATE_API_TOKEN` (required)
  - `OPENAI_API_KEY` (optional)
  - `SHOPIFY_API_KEY` & `SHOPIFY_SECRET` (optional)

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the correct environment
poetry shell  # or source venv/bin/activate

# Install dependencies
poetry install  # or pip install -r requirements.txt
```

### Port already in use
```bash
# Change the port in web_demo.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### API key errors
- Check your `.env` file exists and has correct keys
- Ensure API keys have sufficient credits
- Try with simpler prompts first

## 🎯 Example Products to Try

1. **"Eco-friendly bamboo water bottle with thermal insulation, 500ml capacity"**
2. **"Premium wireless Bluetooth headphones with noise cancellation, 30-hour battery"**
3. **"Organic cotton t-shirt with minimalist design, available in multiple colors"**
4. **"Smart fitness tracker with heart rate monitor, GPS, and 7-day battery"**

## 🚀 Production Deployment

The web demo can be deployed to:
- **Vercel** (serverless functions)
- **Heroku** (containerized)
- **Docker** (containerized)
- **AWS/GCP** (cloud platforms)

## 📞 Support

- Check the main [README.md](README.md) for detailed API documentation
- Report issues on GitHub
- Join our community for questions

---

**Ready to see AI-powered product listing generation in action? 🚀**

Visit `http://localhost:8000` after running the demo!
