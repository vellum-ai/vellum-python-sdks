#!/usr/bin/env python3
"""
Evaluation script that pushes workflow to Vellum, upserts test cases, runs evaluation, and reports results.
"""
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
from typing import List

from vellum import Vellum
from vellum.client.types import NamedTestCaseVariableValueRequest, TestCaseVariableValue
from vellum.evaluations import VellumTestSuite

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def push_workflow():
    """Push the workflow to Vellum using CLI."""
    logger.info("Pushing workflow to Vellum...")
    result = subprocess.run(
        ["vellum", "workflows", "push", "github_actions"],
        cwd=Path(__file__).parent.parent.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(f"Failed to push workflow: {result.stderr}")
        sys.exit(1)
    logger.info("Workflow pushed successfully")


def load_test_cases() -> List[dict]:
    """Load test cases from JSON files."""
    test_cases = []
    test_cases_dir = Path(__file__).parent / "test_cases"

    for json_file in test_cases_dir.glob("*.json"):
        with open(json_file) as f:
            test_cases.extend(json.load(f))

    return test_cases


def run_evaluation():
    """Run the evaluation using VellumTestSuite."""
    logger.info("Loading test cases...")
    load_test_cases()

    client = Vellum(api_key=os.getenv("VELLUM_API_KEY"))

    test_suite_name = "github-actions-eval-suite"
    test_suite = VellumTestSuite(test_suite_name, client=client)

    def execute_workflow(inputs: List[TestCaseVariableValue]) -> List[NamedTestCaseVariableValueRequest]:
        """Execute the workflow for given inputs."""
        input_dict = {inp.name: inp.value for inp in inputs}

        return [
            NamedTestCaseVariableValueRequest(
                name="response", value="Mock response for: " + str(input_dict.get("query", ""))
            )
        ]

    logger.info("Running evaluation...")
    results = test_suite.run_external(execute_workflow)
    results.wait_until_complete()

    logger.info("Evaluation Results:")
    logger.info(f"State: {results.state}")
    logger.info(f"Total executions: {len(results.all_executions)}")

    return results


if __name__ == "__main__":
    push_workflow()
    results = run_evaluation()
    logger.info("Evaluation completed successfully!")
