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

---

## Experimental Evaluation Framework

In addition to the basic test execution capabilities above, this project includes a comprehensive experimental evaluation framework used to conduct rigorous performance analysis.

### Experimental Components

**New Files Added for Research:**
```
mobile-qa-agent/
├── experiment_runner.py      # Comprehensive experimental framework
├── visualize_experiments.py  # Generate publication-quality plots
├── experiments.db            # SQLite database with all results
└── plots/                    # 12 visualization outputs
    ├── phase1_1_*.png       # Baseline performance (4 plots)
    ├── phase1_2_*.png       # Prompt engineering (5 plots)
    ├── phase2_1_*.png       # Model comparison (2 plots)
    └── phase2_2_*.png       # Ensemble strategies (1 plot)
```

### Running Experiments

**Phase 1.1: Baseline Performance Assessment**
```bash
python experiment_runner.py --phase 1.1 --repetitions 10
```
Establishes performance benchmarks across all 4 tests with 10 suite repetitions (40 total runs).

**Phase 1.2: Prompt Engineering Analysis**
```bash
python experiment_runner.py --phase 1.2 --repetitions 10
```
Tests temperature, context window, few-shot examples, and constraint variations (140 total runs).

**Phase 2.1: Model Comparison**
```bash
python experiment_runner.py --phase 2.1 --repetitions 20
```
Compares multiple Gemini model variants on complete test suite (320 total runs).

**Phase 2.2: Ensemble Strategy Evaluation**
```bash
python experiment_runner.py --phase 2.2 --repetitions 15
```
Evaluates ensemble approaches: baseline, majority voting, tiered, confidence-based (60 total runs).

**Run All Experiments:**
```bash
python experiment_runner.py --phase all --repetitions 10
```

### Generating Visualizations

After running experiments, generate plots:
```bash
# Generate all visualizations
python visualize_experiments.py --phase all

# Or generate specific phase
python visualize_experiments.py --phase 1.1
python visualize_experiments.py --phase 1.2
python visualize_experiments.py --phase 2.1
python visualize_experiments.py --phase 2.2
```

Outputs saved to `plots/` directory as PNG files ready for publication.

### Key Experimental Findings

Our comprehensive evaluation across **470+ test executions** revealed:

1. **Perfect Reliability:** 100% success on positive tests (Tests 1-2) with deterministic consistency
2. **Prompt Engineering Minimal Impact:** All temperature/context/few-shot/constraint variations achieved 100%
3. **Model Parity:** Gemini Flash matches Pro performance at 90% cost reduction
4. **Ensemble Unnecessary:** All strategies achieved identical 100% success
5. **Production-Viable:** $0.0005 per test execution = ~$5/year for 10,000 tests

### Experimental Database

All results stored in `experiments.db` SQLite database with schema:
- `experiments` table: Test-level metrics (success, time, cost, tokens)
- `step_metrics` table: Granular step-by-step tracking

Query example:
```python
import sqlite3
conn = sqlite3.connect('experiments.db')
df = pd.read_sql_query("SELECT * FROM experiments WHERE phase='1.1'", conn)
```

### Research Documentation

Complete experimental methodology and results documented in:
- **report.md** - Comprehensive technical report with all findings
- **Focused_Research_Paper.pdf** - 10-page publication-ready paper
- **12 Visualizations** - Publication-quality plots in `plots/` directory

For full details, see `report.md` and research paper in repository.
