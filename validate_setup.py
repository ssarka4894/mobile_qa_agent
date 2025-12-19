#!/usr/bin/env python3
"""
Setup validation script for Mobile QA Agent
Run this to check if everything is configured correctly
"""
import os
import sys
import subprocess
from pathlib import Path

def check_mark(condition):
    return "✅" if condition else "❌"

def main():
    print("\n" + "="*60)
    print("Mobile QA Agent - Setup Validation")
    print("="*60 + "\n")
    
    all_good = True
    
    # Check 1: Python version
    print("1. Checking Python version...")
    py_version = sys.version_info
    if py_version >= (3, 8):
        print(f"   {check_mark(True)} Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        print(f"   {check_mark(False)} Python {py_version.major}.{py_version.minor} (need 3.8+)")
        all_good = False
    print()
    
    # Check 2: .env file
    print("2. Checking .env file...")
    env_exists = Path(".env").exists()
    if env_exists:
        with open(".env", "r") as f:
            content = f.read()
        has_key = "GEMINI_API_KEY=" in content and len(content.split("=")[-1].strip()) > 10
        print(f"   {check_mark(True)} .env file exists")
        if has_key:
            key_preview = content.split("=")[-1].strip()[:20] + "..."
            print(f"   {check_mark(True)} API key found ({key_preview})")
        else:
            print(f"   {check_mark(False)} API key missing or invalid")
            print("   → Edit .env and add: GEMINI_API_KEY=your_key_here")
            all_good = False
    else:
        print(f"   {check_mark(False)} .env file not found")
        print("   → Create .env file: echo 'GEMINI_API_KEY=your_key' > .env")
        all_good = False
    print()
    
    # Check 3: Python dependencies
    print("3. Checking Python dependencies...")
    deps = {
        "google.genai": "google-genai",
        "dotenv": "python-dotenv",
        "PIL": "Pillow"
    }
    
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"   {check_mark(True)} {package}")
        except ImportError:
            print(f"   {check_mark(False)} {package}")
            print(f"   → Install: pip install {package}")
            all_good = False
    print()
    
    # Check 4: ADB
    print("4. Checking ADB (Android Debug Bridge)...")
    try:
        result = subprocess.run(
            ["adb", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   {check_mark(True)} ADB installed: {version}")
            
            # Check devices
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            devices = [line for line in result.stdout.split('\n') 
                      if '\tdevice' in line]
            
            if devices:
                print(f"   {check_mark(True)} {len(devices)} device(s) connected:")
                for device in devices:
                    print(f"      • {device.split()[0]}")
            else:
                print(f"   {check_mark(False)} No devices connected")
                print("   → Connect an Android device or start an emulator")
                all_good = False
        else:
            print(f"   {check_mark(False)} ADB not working properly")
            all_good = False
    except FileNotFoundError:
        print(f"   {check_mark(False)} ADB not found")
        print("   → Install from: https://developer.android.com/studio/releases/platform-tools")
        all_good = False
    except Exception as e:
        print(f"   {check_mark(False)} Error checking ADB: {e}")
        all_good = False
    print()
    
    # Check 5: Project structure
    print("5. Checking project structure...")
    required_dirs = ["agents", "tools", "tests"]
    required_files = ["main.py", "requirements.txt"]
    
    structure_ok = True
    for d in required_dirs:
        exists = Path(d).is_dir()
        print(f"   {check_mark(exists)} {d}/")
        if not exists:
            structure_ok = False
    
    for f in required_files:
        exists = Path(f).is_file()
        print(f"   {check_mark(exists)} {f}")
        if not exists:
            structure_ok = False
    
    if not structure_ok:
        print("   → You may be in the wrong directory")
        print(f"   → Current directory: {Path.cwd()}")
        all_good = False
    print()
    
    # Check 6: Test API connection (optional)
    if env_exists and "GEMINI_API_KEY=" in open(".env").read():
        print("6. Testing Gemini API connection...")
        try:
            from dotenv import load_dotenv
            from google import genai
            
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            
            if api_key:
                client = genai.Client(api_key=api_key)
                # Try a simple request
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Say 'API working' and nothing else"
                )
                if "API working" in response.text or "working" in response.text.lower():
                    print(f"   {check_mark(True)} API connection successful")
                else:
                    print(f"   {check_mark(True)} API responded (check quota)")
            else:
                print(f"   {check_mark(False)} API key not loaded")
                all_good = False
        except Exception as e:
            print(f"   {check_mark(False)} API test failed: {str(e)[:60]}")
            if "quota" in str(e).lower() or "429" in str(e):
                print("   → API quota exceeded - wait 60 seconds")
            elif "401" in str(e) or "403" in str(e):
                print("   → Invalid API key - check .env file")
                all_good = False
            else:
                print(f"   → Error: {str(e)[:100]}")
        print()
    
    # Summary
    print("="*60)
    if all_good:
        print("✅ All checks passed! Ready to run tests.")
        print("\nRun tests with:")
        print("  python main.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  • Create .env:  echo 'GEMINI_API_KEY=your_key' > .env")
        print("  • Install deps: pip install -r requirements.txt")
        print("  • Setup ADB:    Download from developer.android.com")
        print("  • Connect device: adb devices")
    print("="*60 + "\n")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
