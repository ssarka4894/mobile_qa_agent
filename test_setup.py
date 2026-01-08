#!/usr/bin/env python3
"""
Test script to verify experiment framework setup
Run this before starting actual experiments
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_dependencies():
    """Check required packages"""
    print("\n📦 Checking dependencies...")
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib.pyplot',
        'seaborn': 'seaborn',
        'google.genai': 'google-genai',
        'dotenv': 'python-dotenv',
        'PIL': 'Pillow'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Missing")
            missing.append(package)
    
    if missing:
        print(f"\n   Install missing packages:")
        print(f"   pip install {' '.join(missing)} --break-system-packages")
        return False
    return True

def check_project_structure():
    """Check project files exist"""
    print("\n📁 Checking project structure...")
    required_files = [
        'agents/planner.py',
        'agents/executor.py',
        'agents/supervisor.py',
        'tests/test_definitions.py',
        'tools/adb_tools.py',
        'experiment_runner.py',
        'visualize_experiments.py'
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - Missing")
            missing.append(file)
    
    return len(missing) == 0

def check_env_file():
    """Check .env file exists"""
    print("\n🔑 Checking API keys...")
    if Path('.env').exists():
        print("   ✅ .env file exists")
        
        with open('.env') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content:
                print("   ✅ GEMINI_API_KEY found")
                return True
            else:
                print("   ❌ GEMINI_API_KEY not found in .env")
                return False
    else:
        print("   ❌ .env file not found")
        print("   Create .env with: GEMINI_API_KEY=your_key_here")
        return False

def check_adb():
    """Check ADB availability"""
    print("\n📱 Checking ADB...")
    import subprocess
    
    try:
        result = subprocess.run(['adb', 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   ✅ {version}")
            
            # Check device connection
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            devices = [line for line in result.stdout.split('\n') 
                      if '\tdevice' in line]
            
            if devices:
                print(f"   ✅ {len(devices)} device(s) connected")
                for device in devices:
                    device_id = device.split('\t')[0]
                    print(f"      - {device_id}")
                return True
            else:
                print("   ⚠️  No devices connected")
                print("      Connect device via USB or WiFi")
                return False
        else:
            print("   ❌ ADB command failed")
            return False
            
    except FileNotFoundError:
        print("   ❌ ADB not found in PATH")
        print("      Install Android SDK Platform Tools")
        return False
    except subprocess.TimeoutExpired:
        print("   ❌ ADB command timed out")
        return False

def test_database_creation():
    """Test database creation"""
    print("\n🗄️  Testing database...")
    import sqlite3
    
    try:
        # Create test database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute('''
            CREATE TABLE test_experiments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                success BOOLEAN
            )
        ''')
        
        # Insert test data
        cursor.execute('INSERT INTO test_experiments VALUES (1, "test", 1)')
        
        # Query test data
        cursor.execute('SELECT * FROM test_experiments')
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print("   ✅ SQLite working correctly")
            return True
        else:
            print("   ❌ SQLite query failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_visualization():
    """Test basic plotting"""
    print("\n📊 Testing visualization...")
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create simple test plot
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        
        # Try to save (without showing)
        test_dir = Path('test_output')
        test_dir.mkdir(exist_ok=True)
        plt.savefig(test_dir / 'test_plot.png')
        plt.close()
        
        if (test_dir / 'test_plot.png').exists():
            print("   ✅ Plotting working correctly")
            # Cleanup
            (test_dir / 'test_plot.png').unlink()
            test_dir.rmdir()
            return True
        else:
            print("   ❌ Plot file not created")
            return False
            
    except Exception as e:
        print(f"   ❌ Plotting error: {e}")
        return False

def estimate_runtime():
    """Estimate experiment runtime"""
    print("\n⏱️  Experiment Time Estimates:")
    print("   Phase 1.1 (50 reps × 4 tests):")
    print("      ~60s per test × 200 runs = 3.3 hours")
    print("   ")
    print("   Phase 1.2 (10 reps × 11 configs):")
    print("      ~60s per test × 110 runs = 1.8 hours")
    print("   ")
    print("   Phase 2.1 (20 reps × 4 tests × 2 models):")
    print("      ~60s per test × 160 runs = 2.7 hours")
    print("   ")
    print("   Total estimated: 7-8 hours for all experiments")

def main():
    """Run all checks"""
    print("="*70)
    print("EXPERIMENT FRAMEWORK SETUP VERIFICATION")
    print("="*70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Environment Variables", check_env_file),
        ("ADB Connection", check_adb),
        ("Database", test_database_creation),
        ("Visualization", test_visualization),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"\n❌ {name} check failed with exception:")
            print(f"   {str(e)}")
            results.append(False)
    
    estimate_runtime()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for (name, _), result in zip(checks, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Ready to run experiments!")
        print("\nNext steps:")
        print("  1. Review EXPERIMENT_GUIDE.md")
        print("  2. Start with small test: python experiment_runner.py --phase 1.1 --repetitions 2")
        print("  3. Run full experiments: python experiment_runner.py --phase all --repetitions 10")
        print("  4. Generate plots: python visualize_experiments.py --phase all")
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues above")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements_experiments.txt --break-system-packages")
        print("  - Create .env file with GEMINI_API_KEY")
        print("  - Connect Android device via USB")
        print("  - Run from mobile-qa-agent directory")
    print("="*70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
