#!/bin/bash

# Interactive Mobile QA Agent Setup Script

echo "========================================"
echo "   Mobile QA Agent - Interactive Setup"
echo "========================================"
echo ""

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or later."
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check for virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "💡 Tip: Consider using a virtual environment"
    read -p "   Create one now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Virtual environment created and activated"
        echo "   (Run 'source venv/bin/activate' in future sessions)"
        echo ""
    fi
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Setup .env file
echo "🔑 Setting up Gemini API Key..."
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    cat .env
    echo ""
    read -p "   Keep existing file? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        rm .env
        echo "   Deleted existing .env"
    else
        echo "   Keeping existing .env file"
        echo ""
        # Skip to ADB check
        SKIP_ENV=true
    fi
fi

if [ "$SKIP_ENV" != "true" ]; then
    echo ""
    echo "📝 You need a Gemini API key from:"
    echo "   https://aistudio.google.com/app/apikey"
    echo ""
    read -p "   Do you have your API key? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "   Enter your Gemini API key: " API_KEY
        echo "GEMINI_API_KEY=$API_KEY" > .env
        echo "✅ .env file created"
        echo ""
        
        # Verify
        echo "📋 Verifying .env file..."
        if grep -q "GEMINI_API_KEY=" .env && [ ! -z "$API_KEY" ]; then
            echo "✅ API key saved successfully"
        else
            echo "⚠️  API key might be invalid. Please check .env file"
        fi
    else
        echo ""
        echo "⚠️  Please get your API key and create .env file manually:"
        echo "   echo 'GEMINI_API_KEY=your_key_here' > .env"
        cp .env.example .env
        echo "✅ Created .env template"
    fi
fi
echo ""

# Check ADB
echo "📱 Checking ADB (Android Debug Bridge)..."
if ! command -v adb &> /dev/null; then
    echo "⚠️  ADB not found"
    echo "   Download from: https://developer.android.com/studio/releases/platform-tools"
    echo "   After installing, restart this script"
    echo ""
else
    echo "✅ ADB found: $(adb version | head -1)"
    echo ""
    echo "📱 Checking connected devices..."
    DEVICES=$(adb devices | grep -v "List" | grep "device$" | wc -l)
    
    if [ $DEVICES -eq 0 ]; then
        echo "⚠️  No devices connected"
        echo ""
        echo "   To connect a device:"
        echo "   1. Enable USB debugging on your Android device"
        echo "   2. Connect via USB"
        echo "   3. Run: adb devices"
        echo ""
        echo "   Or start an emulator:"
        echo "   - Android Studio → AVD Manager → Start emulator"
        echo ""
    else
        echo "✅ Found $DEVICES device(s):"
        adb devices | grep "device$"
        echo ""
    fi
fi

# Create artifacts directory
mkdir -p artifacts/screenshots
echo "✅ Created artifacts directory"
echo ""

# Final checklist
echo "========================================"
echo "   Setup Checklist"
echo "========================================"
echo ""

# Check .env
if [ -f .env ] && grep -q "GEMINI_API_KEY=..*" .env; then
    echo "✅ .env file with API key"
else
    echo "❌ .env file missing or invalid"
    SETUP_INCOMPLETE=true
fi

# Check dependencies
if python3 -c "import google.genai" 2>/dev/null; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Python dependencies missing"
    SETUP_INCOMPLETE=true
fi

# Check ADB
if command -v adb &> /dev/null; then
    echo "✅ ADB installed"
    if [ $(adb devices | grep -c "device$") -gt 0 ]; then
        echo "✅ Android device connected"
    else
        echo "⚠️  No Android device connected"
        SETUP_INCOMPLETE=true
    fi
else
    echo "❌ ADB not installed"
    SETUP_INCOMPLETE=true
fi

echo ""

if [ "$SETUP_INCOMPLETE" = "true" ]; then
    echo "⚠️  Setup incomplete. Please resolve issues above."
    echo ""
    echo "Quick fixes:"
    echo "  • API key: Edit .env file and add your key"
    echo "  • ADB: Install Android SDK Platform Tools"
    echo "  • Device: Connect Android device or start emulator"
    echo ""
else
    echo "========================================"
    echo "   ✨ Setup Complete!"
    echo "========================================"
    echo ""
    echo "🚀 Ready to run tests!"
    echo ""
    echo "Quick start:"
    echo "  python main.py              # Interactive mode"
    echo "  python main.py --test 1     # Run Test 1"
    echo "  python main.py --all        # Run all tests"
    echo ""
    echo "For detailed help, see:"
    echo "  • README.md - Full documentation"
    echo "  • QUICKSTART.md - Quick reference"
    echo ""
fi
