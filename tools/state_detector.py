"""
State detection utilities for Obsidian mobile app
UPDATED: Compatible with new google.genai SDK
"""
import json
import re
from typing import Dict, List, Optional
from PIL import Image
import base64
import io


class StateDetector:
    """Detects current UI state from screenshots"""
    
    # Define all possible states and their indicators
    STATE_INDICATORS = {
        "welcome_screen": {
            "text_markers": ["Your thoughts are yours", "Create a vault", "Use my existing vault"],
            "description": "Initial Obsidian welcome screen",
            "key_elements": ["create vault button", "purple logo"]
        },
        "sync_setup": {
            "text_markers": ["set up sync", "Continue without sync", "Setup Sync"],
            "description": "Sync configuration prompt",
            "key_elements": ["continue button", "setup sync button"]
        },
        "vault_config": {
            "text_markers": ["Configure your new vault", "Vault name", "Vault location", "Device storage"],
            "description": "Vault configuration form",
            "key_elements": ["text input", "create vault button", "storage selection"]
        },
        "folder_permission": {
            "text_markers": ["Documents", "Use this folder", "No items"],
            "description": "Folder selection for vault storage",
            "key_elements": ["folder icon", "use folder button"]
        },
        "android_permission_dialog": {
            "text_markers": ["Allow Obsidian to access", "Cancel", "Allow"],
            "description": "Android system permission dialog",
            "key_elements": ["allow button", "cancel button", "permission text"]
        },
        "empty_vault": {
            "text_markers": ["New tab", "Create new note", "Close"],
            "description": "Vault opened with no notes",
            "key_elements": ["tab icon", "create note button", "bottom navigation"]
        },
        "note_editor": {
            "text_markers": ["Untitled", "Meeting Notes"],
            "description": "Note editing screen",
            "key_elements": ["keyboard", "editor toolbar", "title field", "body area"]
        },
        "note_menu": {
            "text_markers": ["Close", "Reading view", "Rename", "Source mode"],
            "description": "Note options menu",
            "key_elements": ["menu overlay", "close option", "rename option"]
        },
        "vault_menu": {
            "text_markers": ["Settings", "Vault", "Menu"],
            "description": "Vault navigation menu",
            "key_elements": ["settings option", "vault list"]
        },
        "settings": {
            "text_markers": ["Settings", "Appearance", "Options"],
            "description": "App settings screen",
            "key_elements": ["settings list", "tabs"]
        }
    }
    
    def __init__(self, gemini_client):
        """
        Initialize state detector
        
        Args:
            gemini_client: New Gemini client from google.genai
        """
        self.client = gemini_client
        self.model_id = "gemini-2.5-flash"
        self.state_history: List[Dict] = []
    
    def _image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 for new SDK"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def detect_state(self, screenshot_path: str, previous_state: Optional[str] = None) -> Dict:
        """
        Detect current UI state from screenshot
        
        Args:
            screenshot_path: Path to screenshot file
            previous_state: Previous state for context
            
        Returns:
            {
                "state": "state_name",
                "confidence": 0.0-1.0,
                "visible_elements": [...],
                "text_detected": [...],
                "reasoning": "..."
            }
        """
        try:
            # Build prompt
            prompt = self._build_detection_prompt(previous_state)
            
            # Load image
            img = Image.open(screenshot_path)
            
            # Convert image to bytes for new SDK
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Use new SDK format
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": base64.b64encode(img_bytes).decode('utf-8')
                                }
                            }
                        ]
                    }
                ]
            )
            
            result = self._parse_detection_response(response.text)
            
            # Add to history
            self.state_history.append({
                "state": result["state"],
                "confidence": result["confidence"],
                "screenshot": screenshot_path
            })
            
            return result
            
        except Exception as e:
            print(f"Error detecting state: {e}")
            import traceback
            traceback.print_exc()
            return {
                "state": "unknown",
                "confidence": 0.0,
                "visible_elements": [],
                "text_detected": [],
                "reasoning": f"Detection failed: {str(e)}"
            }
    
    def _build_detection_prompt(self, previous_state: Optional[str]) -> str:
        """Build prompt for state detection"""
        
        states_json = json.dumps(self.STATE_INDICATORS, indent=2)
        
        prompt = f"""Analyze this Obsidian mobile app screenshot and determine the current UI state.

POSSIBLE STATES AND INDICATORS:
{states_json}

{"PREVIOUS STATE: " + previous_state if previous_state else ""}

INSTRUCTIONS:
1. Carefully examine all visible text and UI elements
2. Match against the state indicators above
3. Consider the context of the previous state if provided
4. Look for key distinguishing features of each state

RETURN ONLY VALID JSON (no markdown):
{{
    "state": "state_name",
    "confidence": 0.85,
    "visible_elements": ["button 1", "text field", "icon"],
    "text_detected": ["Create a vault", "Obsidian"],
    "reasoning": "I can see X which indicates Y state"
}}

Be precise and confident in your assessment."""
        
        return prompt
    
    def _parse_detection_response(self, response_text: str) -> Dict:
        """Parse and validate detection response"""
        
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*|\s*```', '', response_text.strip())
        
        try:
            result = json.loads(cleaned)
            
            # Validate required fields
            if "state" not in result:
                result["state"] = "unknown"
            if "confidence" not in result:
                result["confidence"] = 0.5
            if "visible_elements" not in result:
                result["visible_elements"] = []
            if "reasoning" not in result:
                result["reasoning"] = "No reasoning provided"
                
            # Validate state is known
            if result["state"] not in self.STATE_INDICATORS and result["state"] != "unknown":
                print(f"Warning: Unknown state detected: {result['state']}")
                result["state"] = "unknown"
                result["confidence"] = 0.0
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse detection response: {e}")
            print(f"Response text: {response_text}")
            return {
                "state": "unknown",
                "confidence": 0.0,
                "visible_elements": [],
                "text_detected": [],
                "reasoning": f"Parse error: {str(e)}"
            }
    
    def verify_state(self, screenshot_path: str, expected_state: str) -> Dict:
        """
        Verify that screenshot matches expected state
        
        Returns:
            {
                "matches": bool,
                "actual_state": str,
                "confidence": float,
                "message": str
            }
        """
        detected = self.detect_state(screenshot_path)
        
        matches = detected["state"] == expected_state
        confidence = detected["confidence"]
        
        message = ""
        if matches:
            message = f"✓ State matches expected: {expected_state} (confidence: {confidence:.2f})"
        else:
            message = f"✗ State mismatch. Expected: {expected_state}, Got: {detected['state']} (confidence: {confidence:.2f})"
        
        return {
            "matches": matches,
            "actual_state": detected["state"],
            "expected_state": expected_state,
            "confidence": confidence,
            "message": message,
            "details": detected
        }
    
    def get_state_description(self, state_name: str) -> str:
        """Get human-readable description of a state"""
        if state_name in self.STATE_INDICATORS:
            return self.STATE_INDICATORS[state_name]["description"]
        return "Unknown state"
    
    def clear_history(self):
        """Clear state history"""
        self.state_history = []
