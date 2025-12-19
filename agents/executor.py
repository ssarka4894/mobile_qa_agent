"""
Executor Agent: Executes planned actions using ADB
UPDATED: Added support for repeated keyevent actions
"""
import time
from typing import Dict, Any, Optional
from pathlib import Path


class ExecutorAgent:
    """
    The Executor carries out the planned actions using ADB commands
    """
    
    def __init__(self, adb_controller):
        """
        Initialize Executor
        
        Args:
            adb_controller: ADBController instance for device interaction
        """
        self.adb = adb_controller
        self.execution_history: list = []
        self.screenshot_dir = Path("artifacts/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_counter = 0
    
    def execute_action(
        self,
        plan: Dict[str, Any],
        take_screenshot_before: bool = True,
        take_screenshot_after: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a planned action
        
        Args:
            plan: Plan from PlannerAgent
            take_screenshot_before: Whether to take screenshot before action
            take_screenshot_after: Whether to take screenshot after action
            
        Returns:
            {
                "success": bool,
                "action": str,
                "screenshot_before": str,
                "screenshot_after": str,
                "error": str or None,
                "execution_time": float
            }
        """
        action = plan["action"]
        
        print(f"\n{'='*60}")
        print(f"EXECUTOR - Executing: {action}")
        print(f"{'='*60}")
        
        start_time = time.time()
        result = {
            "success": False,
            "action": action,
            "screenshot_before": None,
            "screenshot_after": None,
            "error": None,
            "execution_time": 0.0,
            "plan": plan
        }
        
        try:
            # Take before screenshot
            if take_screenshot_before:
                result["screenshot_before"] = self._take_screenshot("before")
            
            # Execute the action
            if action == "tap":
                success = self._execute_tap(plan)
            elif action == "swipe":
                success = self._execute_swipe(plan)
            elif action == "text":
                success = self._execute_text(plan)
            elif action == "key_combination":
                success = self._execute_key_combination(plan)
            elif action == "keyevent":
                success = self._execute_keyevent(plan)
            elif action == "wait":
                success = self._execute_wait(plan)
            elif action == "verify":
                success = True  # Verification is handled by Supervisor
                print("✓ Verification step (will be handled by Supervisor)")
            elif action == "launch_app":
                success = self._execute_launch_app(plan)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            result["success"] = success
            
            # Wait after action if specified
            wait_after = plan.get("wait_after", 0.5)
            if wait_after > 0 and action != "wait":
                time.sleep(wait_after)
            
            # Take after screenshot
            if take_screenshot_after:
                result["screenshot_after"] = self._take_screenshot("after")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"✗ Execution error: {e}")
        
        result["execution_time"] = time.time() - start_time
        
        # Log execution
        self.execution_history.append(result)
        
        print(f"Execution {'succeeded' if result['success'] else 'failed'}")
        print(f"Time: {result['execution_time']:.2f}s")
        print(f"{'='*60}\n")
        
        return result
    
    def _execute_tap(self, plan: Dict) -> bool:
        """Execute tap action"""
        coords = plan.get("coordinates")
        if not coords or len(coords) != 2:
            print(f"✗ Invalid coordinates: {coords}")
            return False
        
        x, y = coords
        # Don't scale - coordinates are already for Pixel 6 Pro (1440x3120)
        return self.adb.tap(x, y, scale=False)
    
    def _execute_swipe(self, plan: Dict) -> bool:
        """Execute swipe action"""
        start = plan.get("start_coordinates")
        end = plan.get("end_coordinates")
        duration = plan.get("duration_ms", 300)
        
        if not start or not end:
            print(f"✗ Invalid swipe coordinates")
            return False
        
        return self.adb.swipe(
            start[0], start[1],
            end[0], end[1],
            duration_ms=duration,
            scale=False
        )
    
    def _execute_text(self, plan: Dict) -> bool:
        """Execute text input"""
        text = plan.get("text")
        if not text:
            print(f"✗ No text provided")
            return False
        
        return self.adb.type_text(text)
    
    def _execute_key_combination(self, plan: Dict) -> bool:
        """Execute key combination (e.g., Ctrl+A)"""
        keycodes = plan.get("keycodes")
        if not keycodes:
            print(f"✗ No keycodes provided")
            return False
        
        return self.adb.press_key_combination(keycodes)
    
    def _execute_keyevent(self, plan: Dict) -> bool:
        """Execute single key press, with optional repeat"""
        keycode = plan.get("keycode")
        if keycode is None:
            print(f"✗ No keycode provided")
            return False
        
        # Check if we need to repeat the keyevent
        repeat = plan.get("repeat", 1)
        
        if repeat > 1:
            print(f"⌨️  Pressing key {keycode} {repeat} times...")
            for i in range(repeat):
                self.adb.press_key(keycode, wait_after=0.05)
            time.sleep(0.2)  # Small delay after all repeats
            return True
        else:
            return self.adb.press_key(keycode)
    
    def _execute_wait(self, plan: Dict) -> bool:
        """Execute wait"""
        duration = plan.get("duration", 1.0)
        print(f"⏱ Waiting {duration}s...")
        time.sleep(duration)
        return True
    
    def _execute_launch_app(self, plan: Dict) -> bool:
        """Launch an app"""
        package = plan.get("package")
        if not package:
            print(f"✗ No package name provided")
            return False
        
        return self.adb.start_app(package)
    
    def _take_screenshot(self, suffix: str = "") -> str:
        """
        Take and save a screenshot
        
        Args:
            suffix: Suffix to add to filename
            
        Returns:
            Path to screenshot file
        """
        self.screenshot_counter += 1
        filename = f"screenshot_{self.screenshot_counter:04d}_{suffix}.png"
        filepath = self.screenshot_dir / filename
        
        success = self.adb.take_screenshot(str(filepath))
        
        if success:
            return str(filepath)
        return None
    
    def execute_step_with_retry(
        self,
        plan: Dict,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Execute a step with automatic retry on failure
        
        Args:
            plan: Execution plan
            max_retries: Maximum number of retries
            
        Returns:
            Execution result
        """
        retry_count = 0
        last_result = None
        
        while retry_count <= max_retries:
            if retry_count > 0:
                print(f"🔄 Retry attempt {retry_count}/{max_retries}")
                time.sleep(2.0)  # Wait before retry
            
            result = self.execute_action(plan)
            last_result = result
            
            if result["success"]:
                return result
            
            retry_count += 1
        
        # All retries failed
        last_result["retry_count"] = retry_count - 1
        last_result["error"] = f"Failed after {retry_count - 1} retries: {last_result['error']}"
        return last_result
    
    def get_latest_screenshot(self) -> Optional[str]:
        """Get path to most recent screenshot"""
        if self.execution_history:
            last_exec = self.execution_history[-1]
            return last_exec.get("screenshot_after") or last_exec.get("screenshot_before")
        return None
    
    def clear_app_state(self, package_name: str = "md.obsidian") -> bool:
        """
        Clear app data to reset to initial state
        
        Args:
            package_name: App package to clear
            
        Returns:
            Success status
        """
        print(f"🔄 Clearing app data for {package_name}...")
        return self.adb.clear_app_data(package_name)
    
    def get_execution_summary(self) -> Dict:
        """Get summary of all executions"""
        total = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e["success"])
        failed = total - successful
        
        total_time = sum(e["execution_time"] for e in self.execution_history)
        
        return {
            "total_actions": total,
            "successful": successful,
            "failed": failed,
            "total_time": total_time,
            "screenshots_taken": self.screenshot_counter,
            "executions": self.execution_history
        }
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []
        self.screenshot_counter = 0
