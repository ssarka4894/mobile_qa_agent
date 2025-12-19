# QUICKSTART GUIDE

## Step-by-Step Setup (5 minutes)

### Step 1: Create .env File

**Option A - Using command line:**
```bash
cd mobile-qa-agent
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

**Option B - Using text editor:**
```bash
cd mobile-qa-agent
nano .env
```
Then add this line:
```
GEMINI_API_KEY=your_actual_api_key_here
```
Save and exit (Ctrl+X, then Y, then Enter)

### Step 2: Get Your Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Replace `your_actual_api_key_here` in your .env file with the real key

### Step 3: Verify .env File

```bash
cat .env
```
Should show:
```
GEMINI_API_KEY=AIzaSy...  (your actual key)
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Setup ADB

**Check if ADB is installed:**
```bash
adb version
```

**If not installed:**
- Download from: https://developer.android.com/studio/releases/platform-tools
- Extract and add to PATH

**Connect device:**
```bash
adb devices
```
Should show your device/emulator

### Step 6: Run Tests

```bash
python main.py
```

## Troubleshooting

### Error: "Gemini API key not found"

**Solution 1 - Check .env file exists:**
```bash
ls -la .env
cat .env
```

**Solution 2 - Export directly (temporary):**
```bash
export GEMINI_API_KEY="your_key_here"
python main.py
```

**Solution 3 - Check file location:**
Make sure you're in the `mobile-qa-agent` directory:
```bash
pwd  # Should show: .../mobile-qa-agent
```

### Error: "No devices/emulators found"

```bash
# Restart ADB
adb kill-server
adb start-server
adb devices
```

### Error: "ModuleNotFoundError"

Make sure you're in the project root:
```bash
cd mobile-qa-agent
python main.py
```

### Error: "API quota exceeded"

Wait 60 seconds between test runs. The free tier has:
- 10 requests per minute
- 1500 requests per day

## Quick Test

To verify everything is working:

```bash
# 1. Check .env
cat .env

# 2. Check Python
python --version  # Should be 3.8+

# 3. Check ADB
adb devices

# 4. Run a single test
python main.py --test 1
```

## Complete Command Reference

```bash
# Interactive mode (default)
python main.py

# Run specific test
python main.py --test 1    # Create Vault
python main.py --test 2    # Create Note
python main.py --test 3    # Appearance (fails)
python main.py --test 4    # Print PDF (fails)

# Run all tests
python main.py --all

# Run only passing tests
python main.py --passing

# Specify device
python main.py --device emulator-5554
```

## File Locations

```
mobile-qa-agent/
├── .env                    ← YOUR API KEY GOES HERE
├── main.py                 ← RUN THIS
├── requirements.txt        ← Dependencies
├── agents/                 ← AI agents
├── tools/                  ← ADB & detection
└── tests/                  ← Test definitions
```

## Still Having Issues?

Check:
1. ✅ .env file exists in mobile-qa-agent/ directory
2. ✅ .env contains: GEMINI_API_KEY=your_actual_key
3. ✅ No spaces around the = sign
4. ✅ Key is valid (test at https://aistudio.google.com)
5. ✅ Running from mobile-qa-agent/ directory
6. ✅ ADB device connected: `adb devices`
