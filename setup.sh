#!/bin/bash

# Mobile QA Agent Setup Script

echo "================================"
echo "Mobile QA Agent Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or later."
    exit 1
fi
echo "✅ Python found"
echo ""

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Not in a virtual environment. It's recommended to use one."
    read -p "Create virtual environment? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Virtual environment created and activated"
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
else
    echo "✅ .env file exists"
fi
echo ""

# Check ADB
echo "Checking ADB installation..."
adb version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ ADB not found. Please install Android SDK Platform Tools."
    echo "   Download from: https://developer.android.com/studio/releases/platform-tools"
else
    echo "✅ ADB found"
    echo ""
    echo "Connected devices:"
    adb devices
fi
echo ""

# Create artifacts directory
mkdir -p artifacts/screenshots
echo "✅ Created artifacts directory"
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Connect your Android device or start an emulator"
echo "3. Install Obsidian on the device"
echo "4. Run: python main.py"
echo ""
