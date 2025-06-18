#!/usr/bin/env python3
"""
End-to-end testing script for Vellum Workflows SDK.

This script performs comprehensive testing of workflow examples by:
1. Discovering all workflow examples in the repository
2. Loading and executing each workflow with test inputs
3. Validating workflow execution and outputs
4. Generating detailed test reports with success metrics
5. Supporting concurrent execution for efficient testing

Based on the workflows-as-code-runner-prototype repository implementation.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
from typing import Any, Dict, List, Optional, Type, Union

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.outputs import BaseOutputs

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class WorkflowTestCase:
    """Represents a single workflow test case"""

    module_name: str
    workflow_path: str
    test_inputs: Optional[Dict[str, Any]] = None
    expected_outputs: Optional[Dict[str, Any]] = None
    disabled: bool = False


@dataclass
class WorkflowTestResult:
    """Represents the result of testing a single workflow"""

    module_name: str
    success: bool
    execution_time: float
    score: float = 0.0
    error: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None


class WorkflowE2ETester:
    """Main class for running end-to-end workflow tests"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.results: List[WorkflowTestResult] = []

    def discover_workflows(self, examples_dir: str = "examples/workflows") -> List[WorkflowTestCase]:
        """Discover all workflow examples in the repository"""
        workflows: List[WorkflowTestCase] = []
        examples_path = Path(examples_dir)

        if not examples_path.exists():
            logger.warning(f"Examples directory not found: {examples_dir}")
            return workflows

        for workflow_dir in examples_path.iterdir():
            if not workflow_dir.is_dir() or workflow_dir.name.startswith("."):
                continue

            workflow_py = workflow_dir / "workflow.py"
            if not workflow_py.exists():
                continue

            module_name = f"examples.workflows.{workflow_dir.name}"
            workflows.append(WorkflowTestCase(module_name=module_name, workflow_path=str(workflow_py)))

        logger.info(f"Discovered {len(workflows)} workflow examples")
        return workflows

    def load_workflow_class(self, module_name: str) -> Optional[Type[BaseWorkflow]]:
        """Load a workflow class from a module name"""
        try:
            import sys

            current_dir = os.getcwd()
            examples_dir = os.path.join(current_dir, "examples")
            workflows_dir = os.path.join(examples_dir, "workflows")

            for path in [current_dir, examples_dir, workflows_dir]:
                if path not in sys.path:
                    sys.path.insert(0, path)

            return BaseWorkflow.load_from_module(module_name)
        except Exception as e:
            logger.error(f"Failed to load workflow {module_name}: {e}")
            return None

    def get_default_test_inputs(self, workflow_class: Type[BaseWorkflow]) -> Optional[BaseInputs]:
        """Generate default test inputs for a workflow"""
        try:
            inputs_class = workflow_class.get_inputs_class()

            if hasattr(inputs_class, "__annotations__"):
                kwargs: Dict[str, Any] = {}
                for field_name, field_type in inputs_class.__annotations__.items():
                    if field_name.lower() in ["query", "question", "prompt", "text", "input"]:
                        kwargs[field_name] = "What is the weather like today?"
                    elif field_name.lower() in ["message", "content"]:
                        kwargs[field_name] = "Hello, this is a test message."
                    elif field_name.lower() in ["chat_history", "messages"]:
                        from vellum import ChatMessage

                        kwargs[field_name] = [ChatMessage(role="user", text="Hello")]
                    elif field_type == str or str(field_type) == "<class 'str'>":
                        kwargs[field_name] = f"test_{field_name}"
                    elif field_type == int or str(field_type) == "<class 'int'>":
                        kwargs[field_name] = 42
                    elif field_type == float or str(field_type) == "<class 'float'>":
                        kwargs[field_name] = 3.14
                    elif field_type == bool or str(field_type) == "<class 'bool'>":
                        kwargs[field_name] = True
                    else:
                        kwargs[field_name] = f"test_{field_name}"

                return inputs_class(**kwargs)
            else:
                return inputs_class()

        except Exception as e:
            logger.warning(f"Could not generate default inputs for {workflow_class.__name__}: {e}")
            return None

    def execute_workflow_test(self, test_case: WorkflowTestCase) -> WorkflowTestResult:
        """Execute a single workflow test case"""
        start_time = time.time()

        try:
            workflow_class = self.load_workflow_class(test_case.module_name)
            if not workflow_class:
                return WorkflowTestResult(
                    module_name=test_case.module_name,
                    success=False,
                    execution_time=time.time() - start_time,
                    error="Failed to load workflow class",
                )

            workflow = workflow_class()

            test_inputs = None
            if test_case.test_inputs:
                inputs_class = workflow_class.get_inputs_class()
                test_inputs = inputs_class(**test_case.test_inputs)
            else:
                test_inputs = self.get_default_test_inputs(workflow_class)

            if not test_inputs:
                return WorkflowTestResult(
                    module_name=test_case.module_name,
                    success=False,
                    execution_time=time.time() - start_time,
                    error="Could not generate test inputs",
                )

            logger.info(f"Executing workflow: {test_case.module_name}")
            final_event = workflow.run(inputs=test_inputs)

            if final_event.name == "workflow.execution.rejected":
                return WorkflowTestResult(
                    module_name=test_case.module_name,
                    success=False,
                    execution_time=time.time() - start_time,
                    error=f"Workflow rejected: [{final_event.error.code}] {final_event.error.message}",
                )
            elif final_event.name == "workflow.execution.fulfilled":
                outputs = {}
                if hasattr(final_event, "outputs") and final_event.outputs:
                    for output_descriptor, output_value in final_event.outputs:
                        outputs[output_descriptor.name] = output_value

                score = 1.0
                if test_case.expected_outputs:
                    score = self.compare_outputs(outputs, test_case.expected_outputs)

                return WorkflowTestResult(
                    module_name=test_case.module_name,
                    success=True,
                    execution_time=time.time() - start_time,
                    score=score,
                    outputs=outputs,
                )
            else:
                return WorkflowTestResult(
                    module_name=test_case.module_name,
                    success=False,
                    execution_time=time.time() - start_time,
                    error=f"Unexpected final event: {final_event.name}",
                )

        except Exception as e:
            return WorkflowTestResult(
                module_name=test_case.module_name,
                success=False,
                execution_time=time.time() - start_time,
                error=f"Exception during execution: {str(e)}\n{traceback.format_exc()}",
            )

    def compare_outputs(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> float:
        """Compare actual vs expected outputs and return a score"""
        if not expected:
            return 1.0

        total_score = 0.0
        max_score = len(expected)

        for key, expected_value in expected.items():
            if key in actual:
                actual_value = actual[key]
                if actual_value == expected_value:
                    total_score += 1.0
                elif isinstance(expected_value, str) and isinstance(actual_value, str):
                    similarity = len(set(expected_value.split()) & set(actual_value.split())) / max(
                        len(expected_value.split()), len(actual_value.split()), 1
                    )
                    total_score += similarity

        return total_score / max_score if max_score > 0 else 1.0

    def run_tests(self, test_cases: List[WorkflowTestCase]) -> List[WorkflowTestResult]:
        """Run all test cases with concurrent execution"""
        logger.info(f"Running {len(test_cases)} workflow tests with {self.max_workers} workers")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {
                executor.submit(self.execute_workflow_test, test_case): test_case
                for test_case in test_cases
                if not test_case.disabled
            }

            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    status = "✓" if result.success else "✗"
                    logger.info(f"{status} {result.module_name} ({result.execution_time:.2f}s)")
                except Exception as e:
                    logger.error(f"Test execution failed for {test_case.module_name}: {e}")
                    self.results.append(
                        WorkflowTestResult(
                            module_name=test_case.module_name, success=False, execution_time=0.0, error=str(e)
                        )
                    )

        return self.results

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests

        total_time = sum(r.execution_time for r in self.results)
        avg_score = sum(r.score for r in self.results) / total_tests if total_tests > 0 else 0.0

        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
                "total_execution_time": total_time,
                "average_score": avg_score,
            },
            "results": [asdict(result) for result in self.results],
        }

        return report

    def print_summary_table(self):
        """Print a formatted summary table to console"""
        print("\n" + "=" * 80)
        print("WORKFLOW E2E TEST RESULTS")
        print("=" * 80)

        print(f"{'Workflow':<40} {'Status':<10} {'Time':<10} {'Score':<10}")
        print("-" * 80)

        for result in sorted(self.results, key=lambda x: x.module_name):
            status = "PASS" if result.success else "FAIL"
            time_str = f"{result.execution_time:.2f}s"
            score_str = f"{result.score:.2f}" if result.success else "N/A"

            print(f"{result.module_name:<40} {status:<10} {time_str:<10} {score_str:<10}")

        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0

        print("-" * 80)
        print(f"Total: {total_tests}, Passed: {successful_tests}, Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1%}")
        print("=" * 80)


def main():
    """Main entry point for the E2E test script"""
    import argparse

    parser = argparse.ArgumentParser(description="Run end-to-end tests for Vellum Workflows SDK")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of concurrent workers")
    parser.add_argument("--filter", type=str, help="Filter workflows by name substring")
    parser.add_argument("--output", type=str, help="Output JSON report to file")
    parser.add_argument(
        "--examples-dir", type=str, default="examples/workflows", help="Directory containing workflow examples"
    )

    args = parser.parse_args()

    tester = WorkflowE2ETester(max_workers=args.max_workers)

    test_cases = tester.discover_workflows(args.examples_dir)

    if args.filter:
        test_cases = [tc for tc in test_cases if args.filter.lower() in tc.module_name.lower()]
        logger.info(f"Filtered to {len(test_cases)} workflows matching '{args.filter}'")

    if not test_cases:
        logger.error("No workflow test cases found")
        sys.exit(1)

    results = tester.run_tests(test_cases)

    report = tester.generate_report()
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {args.output}")

    tester.print_summary_table()

    failed_tests = sum(1 for r in results if not r.success)
    if failed_tests > 0:
        logger.error(f"{failed_tests} tests failed")
        sys.exit(1)

    logger.info("All tests passed!")
    return 0


if __name__ == "__main__":
    exit(main())
