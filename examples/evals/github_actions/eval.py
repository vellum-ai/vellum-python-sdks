#!/usr/bin/env python3
"""
Evaluation script that upserts test cases, runs evaluation, and reports results.
"""
import json
import logging
import os
from pathlib import Path
from uuid import uuid4
from typing import List

from vellum.client.types.test_suite_run_workflow_sandbox_exec_config_data_request import (
    TestSuiteRunWorkflowSandboxExecConfigDataRequest,
)
from vellum.client.types.test_suite_run_workflow_sandbox_exec_config_request import (
    TestSuiteRunWorkflowSandboxExecConfigRequest,
)
from vellum.client.types.test_suite_test_case_create_bulk_operation_request import (
    TestSuiteTestCaseCreateBulkOperationRequest,
)
from vellum.evaluations.resources import VellumTestSuiteRunResults
from vellum.workflows.vellum_client import create_vellum_client
from vellum_cli.config import load_vellum_cli_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_test_cases() -> List[dict]:
    """Load test cases from JSON files."""
    test_cases = []
    test_cases_dir = Path(__file__).parent / "test_cases"

    for json_file in test_cases_dir.glob("*.json"):
        with open(json_file) as f:
            test_case = json.load(f)
            test_cases.append({"data": test_case, "id": str(uuid4())})

    return test_cases


def run_evaluation():
    """Run the evaluation using VellumTestSuite."""
    logger.info("Loading test cases...")
    test_cases = load_test_cases()

    client = create_vellum_client()
    config = load_vellum_cli_config()
    workflow_sandbox_id = config.workflows[0].workflow_sandbox_id

    test_suite_id = os.getenv("VELLUM_TEST_SUITE_ID")
    if not test_suite_id:
        raise ValueError("`VELLUM_TEST_SUITE_ID` is not set")

    # Ideally, we support the following API to dynamically get a test suite id for a given
    # Workflow Sandbox ID:
    #
    # workflow_sandbox = client.workflow_sandboxes.retrieve(workflow_sandbox_id)
    # test_suite_id = workflow_sandbox.evaluation_reports[0].id

    # vellum push, but for test cases
    client.test_suites.test_suite_test_cases_bulk(
        test_suite_id, request=[TestSuiteTestCaseCreateBulkOperationRequest.model_validate(tc) for tc in test_cases]
    )

    logger.info("Running evaluation...")
    test_suite_run = client.test_suite_runs.create(
        test_suite_id=test_suite_id,
        exec_config=TestSuiteRunWorkflowSandboxExecConfigRequest(
            data=TestSuiteRunWorkflowSandboxExecConfigDataRequest(workflow_sandbox_id=workflow_sandbox_id)
        ),
    )

    results = VellumTestSuiteRunResults(test_suite_run, client=client)
    results.wait_until_complete()

    logger.info("Evaluation Results:")
    logger.info(f"State: {results.state}")
    logger.info(f"Total executions: {len(results.all_executions)}")
    logger.info("Evaluation completed successfully!")

    return results


if __name__ == "__main__":
    results = run_evaluation()
