# Mobile QA Multi-Agent System

Automated testing framework for Obsidian mobile app using AI-powered agents.

## Quick Setup (Recommended)

```bash
# 1. Extract and enter directory
tar -xzf mobile-qa-agent.tar.gz
cd mobile-qa-agent

# 2. Run interactive setup
./setup_interactive.sh

# 3. Validate everything is working
python validate_setup.py

# 4. Run tests!
python main.py
```

For detailed step-by-step instructions, see [QUICKSTART.md](QUICKSTART.md)

## Project Structure

```
mobile-qa-agent/
├── main.py                 # Entry point
├── agents/
│   ├── __init__.py
│   ├── planner.py         # Plans test actions
│   ├── executor.py        # Executes actions via ADB
│   └── supervisor.py      # Verifies results
├── tools/
│   ├── __init__.py
│   ├── adb_tools.py       # ADB controller
│   └── state_detection.py # UI state detection
├── tests/
│   ├── __init__.py
│   ├── test_definitions.py # Test case definitions
│   └── test_runner.py      # Test orchestration
└── requirements.txt
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Ensure ADB is installed:**
   - Install Android SDK Platform Tools
   - Connect your device or start an emulator
   - Verify with: `adb devices`

4. **Install Obsidian on your device/emulator**

## Usage

### Interactive Mode (Default)
```bash
python main.py
```

### Run Specific Test
```bash
python main.py --test 1    # Test 1: Create Vault
python main.py --test 2    # Test 2: Create Note
python main.py --test 3    # Test 3: Appearance Tab (should fail)
python main.py --test 4    # Test 4: Print to PDF (should fail)
```

### Run All Tests
```bash
python main.py --all
```

### Run Only Passing Tests
```bash
python main.py --passing
```

### Specify Device
```bash
python main.py --device emulator-5554
```

## Test Definitions

### Test 1: Create Vault (PASS)
- Opens Obsidian
- Creates a new vault named 'InternVault'
- Handles permissions and sync setup

### Test 2: Create Note (PASS)
- Creates a note titled 'Meeting Notes'
- Adds content: 'Daily Standup'
- Prerequisite: Test 1 must be completed

### Test 3: Verify Appearance Tab Color (FAIL)
- Expected to FAIL
- Checks if Appearance tab icon is red (it's not - it's purple)
- Tests negative validation

### Test 4: Print to PDF (FAIL)
- Expected to FAIL
- Looks for Print to PDF feature (doesn't exist in mobile)
- Tests missing feature detection

## Key Features

- **Lenient State Verification**: Actions don't fail on state mismatches
- **API Quota Handling**: Uses gemini-2.5-flash for higher limits
- **Automatic Retries**: Configurable retry logic for flaky steps
- **Screenshot Capture**: Full visual documentation of test execution
- **Detailed Reports**: Comprehensive test execution reports

## Coordinates Used

All coordinates are for Pixel 6 Pro (1440x3120) resolution.


## Troubleshooting

### "Gemini API key not found"

**Quick Fix:**
```bash
# Create .env file with your API key
echo "GEMINI_API_KEY=your_actual_key_here" > .env

# Verify it was created
cat .env
```

**Get API Key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into .env file

**Still not working?**
```bash
# Run validation script
python validate_setup.py

# Or set environment variable directly
export GEMINI_API_KEY="your_key_here"
python main.py
```

### "No devices/emulators found"
Make sure all files are in the correct directory structure as shown above.

### API Quota Exceeded
The system uses gemini-2.5-flash which has higher quota limits. If you still hit limits, wait 30-60 seconds between test runs.

### State Detection Failures
The supervisor is lenient - state detection failures won't cause test failures unless it's a verify action.

### ADB Connection Issues
```bash
adb kill-server
adb start-server
adb devices
```

## Output

- Test results: `artifacts/Test_X_*.json`
- Screenshots: `artifacts/screenshots/`
- Execution logs: Console output

## Notes

- Tests 1 and 2 are designed to PASS
- Tests 3 and 4 are designed to FAIL (negative testing)
- The system is lenient with state verification to avoid false failures
- Coordinates are hardcoded for reliability
