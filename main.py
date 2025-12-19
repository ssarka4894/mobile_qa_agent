"""
Main entry point for the Mobile QA Multi-Agent System
COMPLETE FILE - Copy this entire file
Updated for new google.genai SDK
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from google import genai
from dotenv import load_dotenv

# Import our modules
from tools.adb_tools import ADBController
from tools.state_detection import StateDetector
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.supervisor import SupervisorAgent
from tests.test_definitions import (
    TEST_1_DEFINITION,
    TEST_2_DEFINITION,
    TEST_3_DEFINITION,
    TEST_4_DEFINITION,
    get_passing_tests,
    get_failing_tests
)
from tests.test_runner import TestRunner


def setup_gemini(api_key: str = None):
    """
    Initialize Gemini AI model using new SDK
    
    Args:
        api_key: Gemini API key (or None to use env var)
        
    Returns:
        Gemini client
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. "
            "Please set GEMINI_API_KEY environment variable or pass api_key parameter"
        )
    
    # Initialize new Gemini client
    client = genai.Client(api_key=api_key)
    
    print("✓ Gemini AI initialized (new SDK)")
    return client


def setup_system(device_id: str = None) -> dict:
    """
    Initialize the complete multi-agent system
    
    Args:
        device_id: Specific Android device ID (or None for auto-detect)
        
    Returns:
        Dict with all system components
    """
    print("\n" + "="*70)
    print("INITIALIZING MOBILE QA MULTI-AGENT SYSTEM")
    print("="*70 + "\n")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Gemini
    gemini_client = setup_gemini()
    
    # Initialize ADB Controller
    print("\nInitializing ADB Controller...")
    adb = ADBController(device_id=device_id)
    
    # Initialize State Detector
    print("\nInitializing State Detector...")
    state_detector = StateDetector(gemini_client)
    
    # Initialize Agents
    print("\nInitializing Agents...")
    planner = PlannerAgent(gemini_client, state_detector)
    print("  ✓ Planner Agent")
    
    executor = ExecutorAgent(adb)
    print("  ✓ Executor Agent")
    
    supervisor = SupervisorAgent(gemini_client, state_detector)
    print("  ✓ Supervisor Agent")
    
    # Initialize Test Runner
    print("\nInitializing Test Runner...")
    test_runner = TestRunner(planner, executor, supervisor, adb)
    print("  ✓ Test Runner")
    
    print("\n" + "="*70)
    print("SYSTEM INITIALIZED SUCCESSFULLY")
    print("="*70 + "\n")
    
    return {
        "gemini_client": gemini_client,
        "adb": adb,
        "state_detector": state_detector,
        "planner": planner,
        "executor": executor,
        "supervisor": supervisor,
        "test_runner": test_runner
    }


def run_single_test(test_number: int = 1, device_id: str = None):
    """
    Run a single test
    
    Args:
        test_number: Test number (1, 2, 3, or 4)
        device_id: Android device ID
    """
    system = setup_system(device_id)
    test_runner = system["test_runner"]
    
    # Select test
    tests = {
        1: TEST_1_DEFINITION,
        2: TEST_2_DEFINITION,
        3: TEST_3_DEFINITION,
        4: TEST_4_DEFINITION
    }
    
    test_def = tests.get(test_number)
    if not test_def:
        print(f"Error: Invalid test number {test_number}")
        return
    
    # Run test
    result = test_runner.run_test(
        test_definition=test_def,
        reset_app_before=True,
        use_hardcoded_steps=True
    )
    
    # Print summary
    print("\n" + "="*70)
    print("TEST EXECUTION COMPLETE")
    print("="*70)
    print(f"Test: {result['test_name']}")
    print(f"Status: {'✓ PASSED' if result['final_result']['passed'] else '✗ FAILED'}")
    print(f"Execution Time: {result['execution_time']:.1f}s")
    print("="*70 + "\n")


def run_passing_tests(device_id: str = None):
    """
    Run Tests 1 and 2 (expected to pass)
    
    Args:
        device_id: Android device ID
    """
    system = setup_system(device_id)
    test_runner = system["test_runner"]
    
    # Run Test 1 and Test 2 as a suite (Test 2 depends on Test 1)
    suite_result = test_runner.run_test_suite(
        test_definitions=[TEST_1_DEFINITION, TEST_2_DEFINITION],
        reset_between_tests=False  # Don't reset between Test 1 and 2
    )
    
    return suite_result


def run_all_tests(device_id: str = None):
    """
    Run all 4 tests
    
    Args:
        device_id: Android device ID
    """
    system = setup_system(device_id)
    test_runner = system["test_runner"]
    
    # Run all tests
    all_tests = [
        TEST_1_DEFINITION,
        TEST_2_DEFINITION,
        TEST_3_DEFINITION,
        TEST_4_DEFINITION
    ]
    
    suite_result = test_runner.run_test_suite(
        test_definitions=all_tests,
        reset_between_tests=True
    )
    
    return suite_result


def run_with_recovery(test_number: int = 1, device_id: str = None):
    """
    Run test with automatic retry/recovery
    
    Args:
        test_number: Test number to run
        device_id: Android device ID
    """
    system = setup_system(device_id)
    test_runner = system["test_runner"]
    
    tests = {
        1: TEST_1_DEFINITION,
        2: TEST_2_DEFINITION,
        3: TEST_3_DEFINITION,
        4: TEST_4_DEFINITION
    }
    
    test_def = tests.get(test_number)
    if not test_def:
        print(f"Error: Invalid test number {test_number}")
        return
    
    result = test_runner.run_test_with_recovery(
        test_definition=test_def,
        max_step_retries=2
    )
    
    return result


def interactive_mode(device_id: str = None):
    """
    Interactive mode for running tests
    
    Args:
        device_id: Android device ID
    """
    system = setup_system(device_id)
    test_runner = system["test_runner"]
    
    while True:
        print("\n" + "="*70)
        print("MOBILE QA MULTI-AGENT SYSTEM - INTERACTIVE MODE")
        print("="*70)
        print("\nOptions:")
        print("  1. Run Test 1 (Create Vault)")
        print("  2. Run Test 2 (Create Note)")
        print("  3. Run Test 3 (Appearance Tab Color - should fail)")
        print("  4. Run Test 4 (Print to PDF - should fail)")
        print("  5. Run Tests 1 & 2 (passing suite)")
        print("  6. Run All Tests")
        print("  7. Clear app data")
        print("  0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            test_runner.run_test(TEST_1_DEFINITION, reset_app_before=True)
        elif choice == "2":
            # For Test 2, ask if vault already exists
            has_vault = input("Does vault 'InternVault' already exist? (y/n): ").lower()
            if has_vault == 'y':
                test_runner.run_test(TEST_2_DEFINITION, reset_app_before=False)
            else:
                print("Running Test 1 first to create vault...")
                test_runner.run_test(TEST_1_DEFINITION, reset_app_before=True)
                test_runner.run_test(TEST_2_DEFINITION, reset_app_before=False)
        elif choice == "3":
            test_runner.run_test(TEST_3_DEFINITION, reset_app_before=False)
        elif choice == "4":
            test_runner.run_test(TEST_4_DEFINITION, reset_app_before=False)
        elif choice == "5":
            test_runner.run_test_suite(
                [TEST_1_DEFINITION, TEST_2_DEFINITION],
                reset_between_tests=False
            )
        elif choice == "6":
            test_runner.run_test_suite(
                [TEST_1_DEFINITION, TEST_2_DEFINITION, TEST_3_DEFINITION, TEST_4_DEFINITION],
                reset_between_tests=False
            )
        elif choice == "7":
            system["executor"].clear_app_state("md.obsidian")
            print("✓ App data cleared")
        else:
            print("Invalid choice, please try again")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Mobile QA Multi-Agent System for Obsidian App Testing"
    )
    parser.add_argument(
        "--test",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run a specific test (1-4)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests"
    )
    parser.add_argument(
        "--passing",
        action="store_true",
        help="Run only passing tests (1 & 2)"
    )
    parser.add_argument(
        "--device",
        type=str,
        help="Specific device ID to use"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--recovery",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run test with automatic recovery"
    )
    
    args = parser.parse_args()
    
    # Determine what to run
    if args.interactive:
        interactive_mode(args.device)
    elif args.test:
        run_single_test(args.test, args.device)
    elif args.all:
        run_all_tests(args.device)
    elif args.passing:
        run_passing_tests(args.device)
    elif args.recovery:
        run_with_recovery(args.recovery, args.device)
    else:
        # Default: interactive mode
        interactive_mode(args.device)


if __name__ == "__main__":
    main()
