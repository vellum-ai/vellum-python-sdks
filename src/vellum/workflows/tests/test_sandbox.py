import pytest
from typing import List

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.sandbox import WorkflowSandboxRunner
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("vellum.workflows.sandbox.load_logger")


@pytest.mark.parametrize(
    ["run_kwargs", "expected_last_log"],
    [
        ({}, "final_results: first"),
        ({"index": 1}, "final_results: second"),
        ({"index": -4}, "final_results: first"),
        ({"index": 100}, "final_results: second"),
    ],
    ids=["default", "specific", "negative", "out_of_bounds"],
)
def test_sandbox_runner__happy_path(mock_logger, run_kwargs, expected_last_log):
    # GIVEN we capture the logs to stdout
    logs = []
    mock_logger.return_value.info.side_effect = lambda msg: logs.append(msg)

    # AND an example workflow
    class Inputs(BaseInputs):
        foo: str

    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            bar = Inputs.foo

    class Workflow(BaseWorkflow[Inputs, BaseState]):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_results = StartNode.Outputs.bar

    # AND a dataset for this workflow
    inputs: List[Inputs] = [
        Inputs(foo="first"),
        Inputs(foo="second"),
    ]

    # WHEN we run the sandbox
    runner = WorkflowSandboxRunner(workflow=Workflow(), inputs=inputs)
    runner.run(**run_kwargs)

    # THEN we see the logs
    assert logs == [
        "Just started Node: StartNode",
        "Just finished Node: StartNode",
        "Workflow fulfilled!",
        "----------------------------------",
        expected_last_log,
    ]
