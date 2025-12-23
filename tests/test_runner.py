"""
Test Runner: Orchestrates test execution using the agent system
"""
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class TestRunner:
    """
    Orchestrates the execution of QA tests using the multi-agent system
    """
    
    def __init__(
        self,
        planner_agent,
        executor_agent,
        supervisor_agent,
        adb_controller
    ):
        """
        Initialize Test Runner
        
        Args:
            planner_agent: PlannerAgent instance
            executor_agent: ExecutorAgent instance
            supervisor_agent: SupervisorAgent instance
            adb_controller: ADBController instance
        """
        self.planner = planner_agent
        self.executor = executor_agent
        self.supervisor = supervisor_agent
        self.adb = adb_controller
        
        self.test_results: List[Dict] = []
        self.artifacts_dir = Path("artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)
    
    def run_test(
        self,
        test_definition: Dict,
        reset_app_before: bool = True,
        use_hardcoded_steps: bool = False
    ) -> Dict[str, Any]:
        """
        Run a single test
        
        Args:
            test_definition: Test definition dict
            reset_app_before: Whether to clear app data before test
            use_hardcoded_steps: Whether to use predefined steps (True) or LLM planning (False)
            
        Returns:
            Test result dict
        """
        test_name = test_definition.get("name")
        print(f"\n{'='*70}")
        print(f"STARTING TEST: {test_name}")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        # Reset app if needed
        if reset_app_before:
            print("🔄 Resetting app state...")
            self.executor.clear_app_state("md.obsidian")
            time.sleep(2)
        
        # Execute test steps
        step_results = []
        step_history = []
        
        for step in test_definition.get("steps", []):
            print(f"\n--- Step {step.get('step_number')}: {step.get('description')} ---")
            
            # Get current screenshot
            current_screenshot = self.executor.get_latest_screenshot()
            if not current_screenshot:
                # Take initial screenshot
                self.executor._take_screenshot("initial")
                current_screenshot = self.executor.get_latest_screenshot()
            
            # Plan next action
            plan = self.planner.plan_next_action(
                current_screenshot=current_screenshot,
                test_objective=test_definition.get("description"),
                current_step=step,
                step_history=step_history,
                use_hardcoded=use_hardcoded_steps
            )
            
            # Execute action
            execution_result = self.executor.execute_action(plan)
            
            # Verify step
            verification_result = self.supervisor.verify_step_execution(
                step_definition=step,
                execution_result=execution_result,
                screenshot_after=execution_result.get("screenshot_after")
            )
            
            # Combine results
            step_result = {
                **step,
                **verification_result,
                "execution_result": execution_result,
                "plan": plan
            }
            
            step_results.append(step_result)
            step_history.append(step_result)
            
            # Stop if critical failure
            if not verification_result["success"] and step.get("critical", False):
                print(f"❌ Critical step failed, stopping test")
                break
        
        # Final verification
        final_screenshot = self.executor.get_latest_screenshot()
        final_result = self.supervisor.verify_test_completion(
            test_definition=test_definition,
            final_screenshot=final_screenshot,
            step_results=step_results
        )
        
        # Generate report
        report = self.supervisor.generate_test_report(
            test_definition=test_definition,
            step_results=step_results,
            final_result=final_result
        )
        
        print("\n" + report)
        
        # Save results
        test_result = {
            "test_name": test_name,
            "test_definition": test_definition,
            "step_results": step_results,
            "final_result": final_result,
            "report": report,
            "execution_time": time.time() - start_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.test_results.append(test_result)
        
        # Save to file
        self._save_test_result(test_result)
        
        return test_result
    
    def run_test_suite(
        self,
        test_definitions: List[Dict],
        reset_between_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Run multiple tests in sequence
        
        Args:
            test_definitions: List of test definition dicts
            reset_between_tests: Whether to reset app between tests
            
        Returns:
            Suite results summary
        """
        print(f"\n{'='*70}")
        print(f"RUNNING TEST SUITE: {len(test_definitions)} tests")
        print(f"{'='*70}\n")
        
        suite_start = time.time()
        results = []
        
        for i, test_def in enumerate(test_definitions, 1):
            print(f"\n>>> Running test {i}/{len(test_definitions)}")
            
            # For Test 2, don't reset (it depends on Test 1)
            should_reset = reset_between_tests and i > 1 and "Test 2" not in test_def.get("name", "")
            
            result = self.run_test(
                test_definition=test_def,
                reset_app_before=should_reset
            )
            
            results.append(result)
            
            # Brief pause between tests
            if i < len(test_definitions):
                time.sleep(3)
        
        # Generate suite summary
        summary = self._generate_suite_summary(results, time.time() - suite_start)
        
        print("\n" + "="*70)
        print("TEST SUITE SUMMARY")
        print("="*70)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✓")
        print(f"Failed: {summary['failed']} ✗")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"Total Time: {summary['total_time']:.1f}s")
        print("="*70 + "\n")
        
        # Save suite results
        self._save_suite_results(summary)
        
        return summary
    
    def _generate_suite_summary(self, results: List[Dict], total_time: float) -> Dict:
        """Generate summary of test suite execution"""
        passed = sum(1 for r in results if r["final_result"]["passed"])
        failed = len(results) - passed
        
        return {
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(results) * 100) if results else 0,
            "total_time": total_time,
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _save_test_result(self, result: Dict):
        """Save individual test result to file"""
        test_name = result["test_name"].replace(" ", "_").replace(":", "")
        filename = f"{test_name}_{result['timestamp'].replace(' ', '_').replace(':', '-')}.json"
        filepath = self.artifacts_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Test result saved: {filepath}")
    
    def _save_suite_results(self, summary: Dict):
        """Save test suite summary"""
        filename = f"test_suite_{summary['timestamp'].replace(' ', '_').replace(':', '-')}.json"
        filepath = self.artifacts_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"💾 Suite results saved: {filepath}")
    
    def run_test_with_recovery(
        self,
        test_definition: Dict,
        max_step_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Run test with automatic recovery on step failures
        
        Args:
            test_definition: Test definition
            max_step_retries: Max retries per step
            
        Returns:
            Test result
        """
        test_name = test_definition.get("name")
        print(f"\n{'='*70}")
        print(f"STARTING TEST WITH RECOVERY: {test_name}")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        # Reset app
        self.executor.clear_app_state("md.obsidian")
        time.sleep(2)
        
        step_results = []
        step_history = []
        
        for step in test_definition.get("steps", []):
            retry_count = 0
            step_success = False
            
            while retry_count <= max_step_retries and not step_success:
                if retry_count > 0:
                    print(f"🔄 Retrying step {step.get('step_number')} (attempt {retry_count + 1})")
                    time.sleep(2)
                
                # Get screenshot
                current_screenshot = self.executor.get_latest_screenshot()
                if not current_screenshot:
                    self.executor._take_screenshot("initial")
                    current_screenshot = self.executor.get_latest_screenshot()
                
                # Plan
                plan = self.planner.plan_next_action(
                    current_screenshot=current_screenshot,
                    test_objective=test_definition.get("description"),
                    current_step=step,
                    step_history=step_history,
                    use_hardcoded=True
                )
                
                # Execute
                execution_result = self.executor.execute_action(plan)
                
                # Verify
                verification_result = self.supervisor.verify_step_execution(
                    step_definition=step,
                    execution_result=execution_result,
                    screenshot_after=execution_result.get("screenshot_after")
                )
                
                step_success = verification_result["success"]
                
                if not step_success:
                    retry_count += 1
                else:
                    # Success
                    step_result = {
                        **step,
                        **verification_result,
                        "execution_result": execution_result,
                        "plan": plan,
                        "retry_count": retry_count
                    }
                    step_results.append(step_result)
                    step_history.append(step_result)
            
            if not step_success:
                print(f"❌ Step {step.get('step_number')} failed after {retry_count} retries")
                # Add failed step to results
                step_result = {
                    **step,
                    "success": False,
                    "retry_count": retry_count,
                    "error": "Max retries exceeded"
                }
                step_results.append(step_result)
                break
        
        # Final verification
        final_screenshot = self.executor.get_latest_screenshot()
        final_result = self.supervisor.verify_test_completion(
            test_definition=test_definition,
            final_screenshot=final_screenshot,
            step_results=step_results
        )
        
        # Generate report
        report = self.supervisor.generate_test_report(
            test_definition=test_definition,
            step_results=step_results,
            final_result=final_result
        )
        
        print("\n" + report)
        
        test_result = {
            "test_name": test_name,
            "test_definition": test_definition,
            "step_results": step_results,
            "final_result": final_result,
            "report": report,
            "execution_time": time.time() - start_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self._save_test_result(test_result)
        
        return test_result
    
    def clear_all_history(self):
        """Clear history from all agents"""
        self.planner.clear_history()
        self.executor.clear_history()
        self.supervisor.clear_history()
        self.test_results = []
        print("🧹 Cleared all agent history")
