"""
QA test case definitions for Obsidian mobile app
FINAL CORRECTED VERSION - Based on actual screenshots
"""
from typing import Dict, List, Any


# Test Case 1: Create Vault - WORKING
TEST_1_DEFINITION = {
    "name": "Test 1: Create Vault",
    "description": "Open Obsidian, create a new Vault named 'InternVault', and enter the vault",
    "expected_result": "PASS",
    "steps": [
        {
            "step_number": 1,
            "description": "Launch Obsidian app",
            "action": "launch_app",
            "package": "md.obsidian",
            "expected_state": "welcome_screen",
            "wait_after": 2.0
        },
        {
            "step_number": 2,
            "description": "Tap 'Create a vault'",
            "from_state": "welcome_screen",
            "expected_state": "sync_setup",
            "action": "tap",
            "coordinates": (550, 1400),
            "wait_after": 1.0
        },
        {
            "step_number": 3,
            "description": "Tap 'Continue without sync'",
            "from_state": "sync_setup",
            "expected_state": "vault_config",
            "action": "tap",
            "coordinates": (550, 1700),
            "wait_after": 1.0
        },
        {
            "step_number": 4,
            "description": "Tap vault name input field",
            "from_state": "vault_config",
            "expected_state": "vault_config",
            "action": "tap",
            "coordinates": (550, 900),
            "wait_after": 0.5
        },
        {
            "step_number": 5,
            "description": "Type vault name 'InternVault'",
            "from_state": "vault_config",
            "expected_state": "vault_config",
            "action": "text",
            "text": "InternVault",
            "wait_after": 0.5
        },
        {
            "step_number": 6,
            "description": "Dismiss keyboard by tapping outside",
            "from_state": "vault_config",
            "expected_state": "vault_config",
            "action": "tap",
            "coordinates": (550, 1000),
            "wait_after": 0.5
        },
        {
            "step_number": 7,
            "description": "Tap 'Create a vault' button",
            "from_state": "vault_config",
            "expected_state": "folder_permission",
            "action": "tap",
            "coordinates": (550, 2500),
            "wait_after": 1.5
        },
        {
            "step_number": 8,
            "description": "Tap 'Use this folder'",
            "from_state": "folder_permission",
            "expected_state": "android_permission_dialog",
            "action": "tap",
            "coordinates": (550, 2900),
            "wait_after": 1.0
        },
        {
            "step_number": 9,
            "description": "Tap 'Allow' for permissions",
            "from_state": "android_permission_dialog",
            "expected_state": "empty_vault",
            "action": "tap",
            "coordinates": (1100, 1800),
            "wait_after": 2.0
        },
        {
            "step_number": 10,
            "description": "Verify vault created and opened",
            "from_state": "empty_vault",
            "expected_state": "empty_vault",
            "action": "verify",
            "verification_criteria": [
                "Screen shows 'Create new note' button",
                "Vault interface is visible",
                "No error messages present"
            ]
        }
    ],
    "success_criteria": [
        "All steps complete without errors",
        "Final state is 'empty_vault'",
        "Vault named 'InternVault' is accessible"
    ]
}


# Test Case 2: Create Note - WORKING
TEST_2_DEFINITION = {
    "name": "Test 2: Create Note",
    "description": "Create a new note titled 'Meeting Notes' and type the text 'Daily Standup' into the body",
    "expected_result": "PASS",
    "prerequisite": "Test 1 must be completed (vault must exist)",
    "steps": [
        {
            "step_number": 1,
            "description": "Tap 'Create new note'",
            "from_state": "empty_vault",
            "expected_state": "note_editor",
            "action": "tap",
            "coordinates": (720, 1500),
            "wait_after": 1.0
        },
        {
            "step_number": 2,
            "description": "Tap on 'Untitled' title field",
            "from_state": "note_editor",
            "expected_state": "note_editor",
            "action": "tap",
            "coordinates": (400, 400),
            "wait_after": 0.3
        },
        {
            "step_number": 3,
            "description": "Delete 'Untitled' text",
            "from_state": "note_editor",
            "expected_state": "note_editor",
            "action": "keyevent",
            "keycode": 67,
            "repeat": 10,
            "wait_after": 0.3
        },
        {
            "step_number": 4,
            "description": "Type note title 'Meeting Notes'",
            "from_state": "note_editor",
            "expected_state": "note_editor",
            "action": "text",
            "text": "Meeting%sNotes",
            "wait_after": 0.5
        },
        {
            "step_number": 5,
            "description": "Tap in note body",
            "from_state": "note_editor",
            "expected_state": "note_editor",
            "action": "tap",
            "coordinates": (720, 1500),
            "wait_after": 0.3
        },
        {
            "step_number": 6,
            "description": "Type note content 'Daily Standup'",
            "from_state": "note_editor",
            "expected_state": "note_editor",
            "action": "text",
            "text": "Daily%sStandup",
            "wait_after": 0.5
        },
        {
            "step_number": 7,
            "description": "Close keyboard",
            "from_state": "note_editor",
            "expected_state": "note_editor",
            "action": "tap",
            "coordinates": (1420, 200),
            "wait_after": 0.5
        },
        {
            "step_number": 8,
            "description": "Open three-dot menu",
            "from_state": "note_editor",
            "expected_state": "note_menu",
            "action": "tap",
            "coordinates": (1300, 300),
            "wait_after": 0.8
        },
        {
            "step_number": 9,
            "description": "Close note and return to main screen",
            "from_state": "note_menu",
            "expected_state": "empty_vault",
            "action": "tap",
            "coordinates": (400, 1400),
            "wait_after": 1.0
        },
        {
            "step_number": 10,
            "description": "Verify note created correctly",
            "from_state": "empty_vault",
            "expected_state": "empty_vault",
            "action": "verify",
            "verification_criteria": [
                "Note titled 'Meeting Notes' was created",
                "Note body contains 'Daily Standup'",
                "Returned to main screen successfully"
            ]
        }
    ],
    "success_criteria": [
        "Note is created successfully",
        "Title is exactly 'Meeting Notes'",
        "Body contains 'Daily Standup'"
    ]
}


# Test Case 3: Verify Appearance Tab Color (SHOULD FAIL) - CORRECTED
TEST_3_DEFINITION = {
    "name": "Test 3: Verify Appearance Tab Color",
    "description": "Go to Settings and verify that the 'Appearance' tab icon is the color Red",
    "expected_result": "FAIL",
    "reason": "The Appearance tab is not red, it's monochrome/default theme color",
    "steps": [
        {
            "step_number": 1,
            "description": "Swipe Vault Menu",
            "from_state": "empty_vault",
            "expected_state": "vault_menu",
            "action": "tap",
            "coordinates": (200, 300),
            "wait_after": 1.0
        },
        {
            "step_number": 2,
            "description": "Open Settings",
            "from_state": "vault_menu",
            "expected_state": "settings",
            "action": "tap",
            "coordinates": (1100, 200),
            "wait_after": 1.0
        },
        {
            "step_number": 3,
            "description": "Create new Note",
            "from_state": "settings",
            "expected_state": "settings",
            "action": "tap",
            "coordinates": (100, 1200),
            "wait_after": 1.0
        },
        {
            "step_number": 4,
            "description": "Verify Appearance icon color (WILL FAIL - not red)",
            "from_state": "settings",
            "expected_state": "settings",
            "action": "verify",
            "verification_criteria": [
                "Appearance tab icon is RED (Expected to FAIL - accent color is purple, not red)"
            ]
        },
        {
            "step_number": 5,
            "description": "Close Settings",
            "from_state": "settings",
            "expected_state": "vault_menu",
            "action": "tap",
            "coordinates": (1300, 300),
            "wait_after": 1.0
        },
        {
            "step_number": 6,
            "description": "Close Vault Menu",
            "from_state": "vault_menu",
            "expected_state": "empty_vault",
            "action": "tap",
            "coordinates": (1300, 300),
            "wait_after": 1.0
        }
    ],
    "success_criteria": [
        "Test should FAIL because Appearance icon/accent color is purple, not red"
    ]
}


# Test Case 4: Print to PDF (SHOULD FAIL) - CORRECTED
TEST_4_DEFINITION = {
    "name": "Test 4: Print to PDF",
    "description": "Find and click the 'Print to PDF' button in the vault options menu",
    "expected_result": "FAIL",
    "reason": "This feature does not exist in the mobile version",
    "steps": [
        {
            "step_number": 1,
            "description": "Tap Vault Options",
            "from_state": "empty_vault",
            "expected_state": "vault_options_menu",
            "action": "tap",
            "coordinates": (1400, 3000),
            "wait_after": 1.0
        },
        {
            "step_number": 2,
            "description": "Look for 'Print to PDF' (not found, menu closes)",
            "from_state": "vault_options_menu",
            "expected_state": "empty_vault",
            "action": "tap",
            "coordinates": (750, 1400),
            "wait_after": 1.0
        },
        {
            "step_number": 3,
            "description": "Verify Print to PDF button exists",
            "from_state": "empty_vault",
            "expected_state": "empty_vault",
            "action": "verify",
            "verification_criteria": [
                "'Print to PDF' button exists in menu (Expected to FAIL - button doesn't exist)"
            ]
        }
    ],
    "success_criteria": [
        "Test should FAIL because 'Print to PDF' doesn't exist in mobile version"
    ]
}


# Complete test suite
TEST_SUITE = {
    "test_1": TEST_1_DEFINITION,
    "test_2": TEST_2_DEFINITION,
    "test_3": TEST_3_DEFINITION,
    "test_4": TEST_4_DEFINITION
}


def get_test(test_name: str) -> Dict[str, Any]:
    """Get test definition by name"""
    return TEST_SUITE.get(test_name)


def get_test_definition(test_id: str) -> Dict[str, Any]:
    """
    Get test definition by ID (for experiment_runner.py compatibility)
    
    Args:
        test_id: Test identifier (e.g., 'test_1', 'test_2', 'test_3', 'test_4')
        
    Returns:
        Test definition dictionary
    """
    return TEST_SUITE.get(test_id)


def get_all_tests() -> List[Dict[str, Any]]:
    """Get all test definitions"""
    return list(TEST_SUITE.values())


def get_passing_tests() -> List[Dict[str, Any]]:
    """Get tests expected to pass"""
    return [t for t in TEST_SUITE.values() if t.get("expected_result") == "PASS"]


def get_failing_tests() -> List[Dict[str, Any]]:
    """Get tests expected to fail"""
    return [t for t in TEST_SUITE.values() if t.get("expected_result") == "FAIL"]
