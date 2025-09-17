#!/bin/bash

# Multi-Agent Product Listing System - Web Demo Runner
# This script starts the local web demo

echo "🤖 Multi-Agent Product Listing System - Web Demo"
echo "=================================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Try Poetry first, then fall back to pip
if command_exists poetry; then
    echo "📦 Attempting to use Poetry for dependency management"
    echo ""

    # Try to install with Poetry
    if poetry install 2>/dev/null; then
        echo "✅ Poetry dependencies installed successfully"
        echo "🚀 Starting web demo with Poetry..."
        echo "📱 Visit: http://localhost:8000"
        echo "❌ To stop: Ctrl+C"
        echo ""
        poetry run python web_demo.py
        exit $?
    else
        echo "⚠️  Poetry setup failed, falling back to pip..."
    fi
fi

# Fallback to pip/virtualenv
echo "📦 Using pip/virtualenv for dependency management"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    if ! python3 -m venv venv 2>/dev/null; then
        echo "❌ Failed to create virtual environment"
        echo "Please install Python 3 and virtualenv:"
        echo "  brew install python3"
        exit 1
    fi
fi

    echo "📦 Activating virtual environment..."
    source venv/bin/activate

    echo "📥 Installing dependencies..."
    if pip install -r requirements.txt; then
        echo "✅ Dependencies installed successfully"
        echo "🚀 Starting web demo..."
        echo "📱 Visit: http://localhost:8000"
        echo "❌ To stop: Ctrl+C"
        echo ""

        # Try the full demo first, fall back to simple demo
        if python web_demo.py 2>/dev/null; then
            echo "✅ Full demo started successfully"
        else
            echo "⚠️  Full demo failed, trying standalone demo..."
            if python simple_demo_standalone.py 2>/dev/null; then
                echo "✅ Standalone demo started successfully"
            else
                echo "⚠️  Standalone demo failed, trying static HTML..."
                echo "📄 Opening static demo in browser..."
                echo "   File: $(pwd)/static_demo.html"
                echo "   Or just double-click the file in your file manager"
                echo ""
                echo "🎉 Static demo is ready! Open static_demo.html in your browser."
                exit 0
            fi
        fi
    else
        echo "❌ Failed to install dependencies"
        echo ""
        echo "🔧 Troubleshooting:"
        echo "1. Make sure you have Python 3.8+ installed"
        echo "2. Try: pip install --upgrade pip"
        echo "3. Check your internet connection"
        echo "4. Try manual installation: pip install fastapi uvicorn jinja2"
        exit 1
    fi
