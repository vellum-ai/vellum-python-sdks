import pytest
from typing import List

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.sandbox.runner import SandboxRunner
from vellum.workflows.sandbox.types import Datapoint
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("vellum.workflows.sandbox.runner.load_logger")


@pytest.mark.parametrize(
    ["datapoint", "expected_first_log", "expected_last_log"],
    [
        (None, "Running dataset: first", "final_results: first"),
        ("second", "Running dataset: second", "final_results: second"),
    ],
    ids=["default", "specific"],
)
def test_sandbox_runner__happy_path(mock_logger, datapoint, expected_first_log, expected_last_log):
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
            final_results = Inputs.foo

    # AND a dataset for this workflow
    dataset: List[Datapoint[Inputs]] = [
        Datapoint(
            name="first",
            inputs=Inputs(foo="first"),
        ),
        Datapoint(
            name="second",
            inputs=Inputs(foo="second"),
        ),
    ]

    # WHEN we run the sandbox
    runner = SandboxRunner(Workflow, dataset)
    runner.run(datapoint=datapoint)

    # THEN we see the logs
    assert logs == [
        expected_first_log,
        "Just started Node: StartNode",
        "Just finished Node: StartNode",
        "Workflow fulfilled!",
        "----------------------------------",
        expected_last_log,
    ]
