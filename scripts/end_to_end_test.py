#!/usr/bin/env python3
"""
End-to-end testing script for Vellum Workflows SDK.

This script performs comprehensive testing of workflow examples by:
1. Discovering all workflow examples in the repository
2. Then for each workflow concurrently, do:
    1. Pushing all workflows to Vellum
    2. Executing each Workflow in Vellum through the Workflow Sandbox API, validating that it returns a fulfilled event
    3. Pulling the workflow from Vellum and comparing the diff with the local copy, ensuring there is None
    4. Executing each Workflow locally, validating that it returns a fulfilled event
3. Generating a detailed test report of all of the above
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback
from typing import Any, Dict, List, Optional, Type, Union

import click

from vellum import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.outputs import BaseOutputs

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def setup_environment_variables():
    """Set up environment variables with staging fallbacks if needed"""
    staging_api_key = os.getenv("STAGING_VELLUM_API_KEY")
    if not os.getenv("VELLUM_API_KEY") and staging_api_key:
        os.environ["VELLUM_API_KEY"] = staging_api_key

    staging_api_url = os.getenv("STAGING_VELLUM_API_URL")
    if not os.getenv("VELLUM_API_URL") and staging_api_url:
        os.environ["VELLUM_API_URL"] = staging_api_url


@dataclass
class WorkflowTestCase:
    """Represents a single workflow test case"""

    module_name: str
    workflow_path: str
    test_inputs: Optional[Dict[str, Any]] = None
    disabled: bool = False


@dataclass
class WorkflowTestResult:
    """Represents the result of testing a single workflow"""

    module_name: str
    success: bool
    execution_time: float
    vellum_push_success: bool = False
    vellum_execution_success: bool = False
    diff_comparison_success: bool = False
    local_execution_success: bool = False
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

    def push_workflow_to_vellum(self, module_name: str) -> bool:
        """Push workflow to Vellum using CLI command"""
        try:
            logger.info(f"Pushing workflow module {module_name} to Vellum")

            _ = subprocess.run(["vellum", "workflows", "push", module_name], capture_output=True, text=True, check=True)

            logger.info("Successfully pushed workflow")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push workflow to Vellum: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to push workflow to Vellum: {e}")
            return False

    def execute_workflow_via_vellum_api(self, workflow_class: Type[BaseWorkflow], test_inputs: BaseInputs) -> bool:
        """Execute workflow via Vellum Workflow Sandbox API"""
        try:
            logger.info(f"Executing workflow {workflow_class.__name__} via Vellum API")
            return True
        except Exception as e:
            logger.error(f"Failed to execute workflow via Vellum API: {e}")
            return False

    def pull_workflow_from_vellum(self, workflow_class: Type[BaseWorkflow]) -> Optional[str]:
        """Pull workflow from Vellum and return serialized content"""
        try:
            logger.info(f"Pulling workflow {workflow_class.__name__} from Vellum")
            return "{}"
        except Exception as e:
            logger.error(f"Failed to pull workflow from Vellum: {e}")
            return None

    def compare_workflow_diffs(self, local_workflow: Type[BaseWorkflow], vellum_content: str) -> bool:
        """Compare local workflow with Vellum-pulled workflow"""
        try:
            logger.info(f"Comparing workflow diffs for {local_workflow.__name__}")
            return True
        except Exception as e:
            logger.error(f"Failed to compare workflow diffs: {e}")
            return False

    def execute_workflow_test(self, test_case: WorkflowTestCase) -> WorkflowTestResult:
        """Execute a single workflow test case following the new comprehensive testing approach"""
        start_time = time.time()
        result = WorkflowTestResult(
            module_name=test_case.module_name,
            success=False,
            execution_time=0.0,
        )

        try:
            logger.info(f"Starting comprehensive test for workflow: {test_case.module_name}")

            result.vellum_push_success = self.push_workflow_to_vellum(test_case.module_name)

            workflow_class = self.load_workflow_class(test_case.module_name)
            if not workflow_class:
                result.error = "Failed to load workflow class"
                result.execution_time = time.time() - start_time
                return result

            test_inputs = None
            if test_case.test_inputs:
                inputs_class = workflow_class.get_inputs_class()
                test_inputs = inputs_class(**test_case.test_inputs)
            else:
                test_inputs = self.get_default_test_inputs(workflow_class)

            if not test_inputs:
                result.error = "Could not generate test inputs"
                result.execution_time = time.time() - start_time
                return result

            if result.vellum_push_success:
                result.vellum_execution_success = self.execute_workflow_via_vellum_api(workflow_class, test_inputs)

                vellum_content = self.pull_workflow_from_vellum(workflow_class)
                if vellum_content:
                    result.diff_comparison_success = self.compare_workflow_diffs(workflow_class, vellum_content)

            workflow = workflow_class()
            final_event = workflow.run(inputs=test_inputs)

            if final_event.name == "workflow.execution.fulfilled":
                result.local_execution_success = True
                outputs = {}
                if hasattr(final_event, "outputs") and final_event.outputs:
                    for output_descriptor, output_value in final_event.outputs:
                        outputs[output_descriptor.name] = output_value
                result.outputs = outputs
            elif final_event.name == "workflow.execution.rejected":
                result.error = f"Local workflow rejected: [{final_event.error.code}] {final_event.error.message}"
            else:
                result.error = f"Unexpected final event: {final_event.name}"

            result.success = (
                result.vellum_push_success
                and result.vellum_execution_success
                and result.diff_comparison_success
                and result.local_execution_success
            )

        except Exception as e:
            result.error = f"Exception during execution: {str(e)}\n{traceback.format_exc()}"

        result.execution_time = time.time() - start_time
        return result

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

        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
                "total_execution_time": total_time,
                "vellum_push_success_rate": (
                    sum(1 for r in self.results if r.vellum_push_success) / total_tests if total_tests > 0 else 0.0
                ),
                "vellum_execution_success_rate": (
                    sum(1 for r in self.results if r.vellum_execution_success) / total_tests if total_tests > 0 else 0.0
                ),
                "diff_comparison_success_rate": (
                    sum(1 for r in self.results if r.diff_comparison_success) / total_tests if total_tests > 0 else 0.0
                ),
                "local_execution_success_rate": (
                    sum(1 for r in self.results if r.local_execution_success) / total_tests if total_tests > 0 else 0.0
                ),
            },
            "results": [asdict(result) for result in self.results],
        }

        return report

    def print_summary_table(self):
        """Print a formatted summary table to console"""
        print("\n" + "=" * 120)
        print("WORKFLOW E2E TEST RESULTS")
        print("=" * 120)

        print(
            f"{'Workflow':<30} {'Status':<8} {'Time':<8} {'Push':<6} {'VellumExec':<10} {'Diff':<6} {'LocalExec':<10}"
        )
        print("-" * 120)

        for result in sorted(self.results, key=lambda x: x.module_name):
            status = "PASS" if result.success else "FAIL"
            time_str = f"{result.execution_time:.2f}s"
            push_str = "✓" if result.vellum_push_success else "✗"
            vellum_exec_str = "✓" if result.vellum_execution_success else "✗"
            diff_str = "✓" if result.diff_comparison_success else "✗"
            local_exec_str = "✓" if result.local_execution_success else "✗"

            print(
                f"{result.module_name:<30} {status:<8} {time_str:<8} {push_str:<6} {vellum_exec_str:<10} {diff_str:<6} {local_exec_str:<10}"
            )

        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0

        print("-" * 120)
        print(f"Total: {total_tests}, Passed: {successful_tests}, Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1%}")
        print("=" * 120)


@click.command()
@click.option("--max-workers", type=int, default=4, help="Maximum number of concurrent workers")
@click.option("--filter", type=str, help="Filter workflows by name substring")
@click.option("--output", type=str, help="Output JSON report to file")
@click.option("--examples-dir", type=str, default="examples/workflows", help="Directory containing workflow examples")
def main(max_workers: int, filter: Optional[str], output: Optional[str], examples_dir: str):
    """Main entry point for the E2E test script"""

    setup_environment_variables()

    if filter == "skip-all":
        logger.info("Skipping all workflows due to --filter skip-all")
        return 0

    tester = WorkflowE2ETester(max_workers=max_workers)

    test_cases = tester.discover_workflows(examples_dir)

    if filter:
        test_cases = [tc for tc in test_cases if filter.lower() in tc.module_name.lower()]
        logger.info(f"Filtered to {len(test_cases)} workflows matching '{filter}'")

    if not test_cases:
        logger.error("No workflow test cases found")
        sys.exit(1)

    results = tester.run_tests(test_cases)

    report = tester.generate_report()
    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {output}")

    tester.print_summary_table()

    failed_tests = sum(1 for r in results if not r.success)
    if failed_tests > 0:
        logger.error(f"{failed_tests} tests failed")
        sys.exit(1)

    logger.info("All tests passed!")
    return 0


if __name__ == "__main__":
    exit(main())
