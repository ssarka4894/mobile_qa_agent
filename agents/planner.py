"""
Planner Agent: Decides what action to take based on current state and test objective
UPDATED: Compatible with new google.genai SDK
"""
import json
import re
import base64
import io
from typing import Dict, List, Optional, Any
from PIL import Image


class PlannerAgent:
    """
    The Planner analyzes the current state and determines the next action
    to progress toward the test objective.
    """
    
    def __init__(self, gemini_client, state_detector):
        """
        Initialize Planner
        
        Args:
            gemini_client: New Gemini client from google.genai
            state_detector: StateDetector instance for state detection
        """
        self.client = gemini_client
        self.model_id = "gemini-2.5-flash"
        self.state_detector = state_detector
        self.planning_history: List[Dict] = []
    
    def plan_next_action(
        self,
        current_screenshot: str,
        test_objective: str,
        current_step: Dict[str, Any],
        step_history: List[Dict],
        use_hardcoded: bool = True
    ) -> Dict[str, Any]:
        """
        Plan the next action based on current state and objective
        
        Args:
            current_screenshot: Path to current screenshot
            test_objective: Overall test objective
            current_step: Current step definition from test
            step_history: History of previous steps
            use_hardcoded: Whether to use hardcoded step definition (True) or LLM reasoning (False)
            
        Returns:
            {
                "action": "tap|swipe|text|key_combination|wait|verify",
                "coordinates": (x, y),  # if tap/swipe
                "text": "...",          # if text input
                "keycodes": [...],      # if key_combination
                "duration": 1.0,        # if wait
                "reasoning": "...",
                "expected_next_state": "...",
                "confidence": 0.0-1.0
            }
        """
        # Detect current state
        detected_state = self.state_detector.detect_state(
            current_screenshot,
            previous_state=step_history[-1]["actual_state"] if step_history else None
        )
        
        print(f"\n{'='*60}")
        print(f"PLANNER - Step {current_step.get('step_number', '?')}")
        print(f"{'='*60}")
        print(f"Objective: {test_objective}")
        print(f"Current State: {detected_state['state']} (confidence: {detected_state['confidence']:.2f})")
        print(f"Step Description: {current_step.get('description', 'N/A')}")
        
        if use_hardcoded:
            # Use the predefined step definition
            plan = self._create_plan_from_step(current_step, detected_state)
        else:
            # Use LLM to dynamically plan
            plan = self._plan_with_llm(
                current_screenshot,
                test_objective,
                current_step,
                detected_state,
                step_history
            )
        
        # Log this plan
        self.planning_history.append({
            "step": current_step.get('step_number'),
            "detected_state": detected_state['state'],
            "plan": plan
        })
        
        print(f"Planned Action: {plan['action']}")
        if 'coordinates' in plan:
            print(f"Coordinates: {plan['coordinates']}")
        if 'text' in plan:
            print(f"Text: {plan['text']}")
        print(f"Reasoning: {plan['reasoning']}")
        print(f"{'='*60}\n")
        
        return plan
    
    def _create_plan_from_step(self, step: Dict, detected_state: Dict) -> Dict[str, Any]:
        """Create plan directly from step definition"""
        
        action = step.get('action')
        plan = {
            "action": action,
            "reasoning": f"Executing predefined step: {step.get('description')}",
            "expected_next_state": step.get('expected_state', 'unknown'),
            "confidence": 1.0,
            "step_definition": step
        }
        
        # Add action-specific parameters
        if action == 'tap':
            plan['coordinates'] = step.get('coordinates')
        elif action == 'swipe':
            plan['start_coordinates'] = step.get('start_coordinates')
            plan['end_coordinates'] = step.get('end_coordinates')
            plan['duration_ms'] = step.get('duration_ms', 300)
        elif action == 'text':
            plan['text'] = step.get('text')
        elif action == 'key_combination':
            plan['keycodes'] = step.get('keycodes')
        elif action == 'keyevent':
            plan['keycode'] = step.get('keycode')
            plan['repeat'] = step.get('repeat', 1)
        elif action == 'wait':
            plan['duration'] = step.get('duration', 1.0)
        elif action == 'verify':
            plan['verification_criteria'] = step.get('verification_criteria', [])
        elif action == 'launch_app':
            plan['package'] = step.get('package')
        
        return plan
    
    def _plan_with_llm(
        self,
        screenshot_path: str,
        test_objective: str,
        current_step: Dict,
        detected_state: Dict,
        step_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Use LLM to dynamically plan the next action
        This is useful for adaptive behavior when hardcoded steps don't work
        """
        
        img = Image.open(screenshot_path)
        
        # Build context from history
        history_context = self._build_history_context(step_history)
        
        prompt = f"""You are a QA automation planner for mobile app testing.

TEST OBJECTIVE: {test_objective}

CURRENT STATE:
- Detected State: {detected_state['state']}
- Confidence: {detected_state['confidence']}
- Visible Elements: {', '.join(detected_state.get('visible_elements', []))}

CURRENT STEP:
- Description: {current_step.get('description')}
- Expected State After: {current_step.get('expected_state')}

STEP HISTORY:
{history_context}

INSTRUCTIONS:
1. Analyze the screenshot to understand what's currently visible
2. Determine the best action to progress toward the step objective
3. Consider the current state and what actions are valid
4. If the expected state is already reached, plan a verification action

AVAILABLE ACTIONS:
- tap: Tap at coordinates
- swipe: Swipe gesture
- text: Type text
- key_combination: Press key combination (e.g., Ctrl+A)
- keyevent: Press single key
- wait: Wait for duration
- verify: Verify something on screen

Return ONLY valid JSON:
{{
    "action": "tap|swipe|text|key_combination|keyevent|wait|verify",
    "coordinates": [x, y],              // for tap (required)
    "start_coordinates": [x, y],        // for swipe (required)
    "end_coordinates": [x, y],          // for swipe (required)
    "text": "text to type",             // for text (use %s for spaces)
    "keycodes": [113, 29],              // for key_combination
    "keycode": 66,                      // for keyevent
    "duration": 1.0,                    // for wait
    "verification_criteria": ["..."],   // for verify
    "reasoning": "why this action",
    "expected_next_state": "state_name",
    "confidence": 0.85
}}

Be precise with coordinates. The screen dimensions are visible in the image."""
        
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Use new SDK
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
            
            plan = self._parse_plan_response(response.text)
            return plan
            
        except Exception as e:
            print(f"Error in LLM planning: {e}")
            # Fallback: use step definition
            return self._create_plan_from_step(current_step, detected_state)
    
    def _build_history_context(self, step_history: List[Dict]) -> str:
        """Build readable context from step history"""
        if not step_history:
            return "No previous steps"
        
        context_lines = []
        for i, step in enumerate(step_history[-5:], 1):  # Last 5 steps
            status = "✓" if step.get("success", False) else "✗"
            context_lines.append(
                f"{status} Step {step.get('step_number', i)}: "
                f"{step.get('description', 'N/A')} "
                f"(State: {step.get('actual_state', 'unknown')})"
            )
        
        return "\n".join(context_lines)
    
    def _parse_plan_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into plan"""
        
        # Remove markdown code blocks
        cleaned = re.sub(r'```json\s*|\s*```', '', response_text.strip())
        
        try:
            plan = json.loads(cleaned)
            
            # Validate required fields
            if "action" not in plan:
                raise ValueError("Plan missing 'action' field")
            
            # Set defaults
            if "reasoning" not in plan:
                plan["reasoning"] = "No reasoning provided"
            if "confidence" not in plan:
                plan["confidence"] = 0.5
            if "expected_next_state" not in plan:
                plan["expected_next_state"] = "unknown"
            
            return plan
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse plan response: {e}")
            print(f"Response: {response_text}")
            raise
    
    def should_retry_step(self, step_result: Dict, max_retries: int = 2) -> bool:
        """
        Determine if a failed step should be retried
        
        Args:
            step_result: Result from previous step execution
            max_retries: Maximum number of retries allowed
            
        Returns:
            True if should retry
        """
        if step_result.get("success", False):
            return False
        
        retry_count = step_result.get("retry_count", 0)
        if retry_count >= max_retries:
            return False
        
        # Retry if it was a timing issue or minor failure
        failure_reason = step_result.get("error", "")
        
        # Don't retry on fundamental issues
        if "element not found" in failure_reason.lower():
            return False
        if "state mismatch" in failure_reason.lower() and retry_count > 0:
            return False
        
        return True
    
    def adapt_plan_for_retry(self, original_plan: Dict, failure_info: Dict) -> Dict:
        """
        Adapt a plan for retry based on failure information
        
        Args:
            original_plan: The original plan that failed
            failure_info: Information about why it failed
            
        Returns:
            Modified plan
        """
        adapted_plan = original_plan.copy()
        
        # Increase wait times
        if "wait_after" in adapted_plan:
            adapted_plan["wait_after"] *= 1.5
        
        # Add extra wait before action
        adapted_plan["wait_before"] = 1.0
        
        # Note this is a retry
        adapted_plan["is_retry"] = True
        adapted_plan["reasoning"] += " (RETRY with longer waits)"
        
        return adapted_plan
    
    def get_planning_summary(self) -> Dict:
        """Get summary of planning decisions made"""
        return {
            "total_plans": len(self.planning_history),
            "plans": self.planning_history
        }
    
    def clear_history(self):
        """Clear planning history"""
        self.planning_history = []
