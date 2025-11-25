import pytest
from datetime import datetime
from unittest.mock import MagicMock
from typing import List

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.sandbox import WorkflowSandboxRunner
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers import ScheduleTrigger
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


def test_sandbox_runner_with_dict_inputs(mock_logger):
    """
    Test that WorkflowSandboxRunner can run with dict inputs in DatasetRow.
    """

    # GIVEN we capture the logs to stdout
    logs = []
    mock_logger.return_value.info.side_effect = lambda msg: logs.append(msg)

    class Inputs(BaseInputs):
        message: str

    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result = Inputs.message

    class Workflow(BaseWorkflow[Inputs, BaseState]):
        graph = StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = StartNode.Outputs.result

    dataset = [
        DatasetRow(label="test_row", inputs={"message": "Hello from dict"}),
    ]

    # WHEN we run the sandbox with the DatasetRow containing dict inputs
    runner = WorkflowSandboxRunner(workflow=Workflow(), dataset=dataset)
    runner.run()

    assert logs == [
        "Just started Node: StartNode",
        "Just finished Node: StartNode",
        "Workflow fulfilled!",
        "----------------------------------",
        "final_output: Hello from dict",
    ]


def test_sandbox_runner_with_workflow_trigger(mock_logger):
    """
    Test that WorkflowSandboxRunner can run with DatasetRow containing workflow_trigger.
    """

    # GIVEN we capture the logs to stdout
    logs = []
    mock_logger.return_value.info.side_effect = lambda msg: logs.append(msg)

    class MySchedule(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "* * * * *"
            timezone = "UTC"

    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result = MySchedule.current_run_at

    class Workflow(BaseWorkflow):
        graph = MySchedule >> StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = StartNode.Outputs.result

    # AND a trigger instance
    trigger_instance = MySchedule(current_run_at=datetime.min, next_run_at=datetime.now())

    # AND a dataset with workflow_trigger instance
    dataset = [
        DatasetRow(
            label="test_row",
            inputs={"current_run_at": datetime.min, "next_run_at": datetime.now()},
            workflow_trigger=trigger_instance,
        ),
    ]

    # WHEN we run the sandbox with the DatasetRow containing workflow_trigger
    runner = WorkflowSandboxRunner(workflow=Workflow(), dataset=dataset)
    runner.run()

    # THEN the workflow should run successfully
    assert logs == [
        "Just started Node: StartNode",
        "Just finished Node: StartNode",
        "Workflow fulfilled!",
        "----------------------------------",
        "final_output: 0001-01-01 00:00:00",
    ]

    # AND the dataset row should have the trigger instance
    assert dataset[0].workflow_trigger == trigger_instance
    assert isinstance(dataset[0].workflow_trigger, MySchedule)


def test_sandbox_runner_with_trigger_instance(mock_logger):
    """
    Test that WorkflowSandboxRunner can run with DatasetRow containing trigger instance.
    """

    # GIVEN we capture the logs to stdout
    logs = []
    mock_logger.return_value.info.side_effect = lambda msg: logs.append(msg)

    # AND a trigger class
    class MySchedule(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "* * * * *"
            timezone = "UTC"

    # AND a workflow that uses the trigger
    class StartNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result = MySchedule.current_run_at

    class Workflow(BaseWorkflow):
        graph = MySchedule >> StartNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = StartNode.Outputs.result

    # AND a trigger instance
    trigger_instance = MySchedule(current_run_at=datetime.min, next_run_at=datetime.now())

    # AND a dataset with trigger instance
    dataset = [
        DatasetRow(
            label="test_row_with_instance",
            inputs={"current_run_at": datetime.min, "next_run_at": datetime.now()},
            workflow_trigger=trigger_instance,
        ),
    ]

    # WHEN we run the sandbox with the DatasetRow containing trigger instance
    runner = WorkflowSandboxRunner(workflow=Workflow(), dataset=dataset)
    runner.run()

    # THEN the workflow should run successfully
    assert logs == [
        "Just started Node: StartNode",
        "Just finished Node: StartNode",
        "Workflow fulfilled!",
        "----------------------------------",
        "final_output: 0001-01-01 00:00:00",
    ]

    # AND the dataset row should have the trigger instance
    assert dataset[0].workflow_trigger == trigger_instance
    assert isinstance(dataset[0].workflow_trigger, MySchedule)


def test_dataset_row_serialization_with_workflow_trigger():
    """
    Test that DatasetRow serializes workflow_trigger field to workflow_trigger_id.
    """

    # GIVEN a trigger class
    class MySchedule(ScheduleTrigger):
        class Config(ScheduleTrigger.Config):
            cron = "* * * * *"
            timezone = "UTC"

    # AND a trigger instance
    trigger_instance = MySchedule(current_run_at=datetime.min, next_run_at=datetime.now())

    # AND a DatasetRow constructed with workflow_trigger
    dataset_row = DatasetRow(
        label="test_serialization",
        inputs={"foo": "bar"},
        workflow_trigger=trigger_instance,
    )

    # WHEN we serialize the DatasetRow
    serialized = dataset_row.model_dump()

    # THEN the serialized dict should contain workflow_trigger_id
    assert "workflow_trigger_id" in serialized
    assert serialized["workflow_trigger_id"] == str(MySchedule.__id__)


def test_sandbox_runner_with_node_output_mocks(mock_logger, mocker):
    """
    Tests that WorkflowSandboxRunner passes mocks from DatasetRow to workflow.stream().
    """

    class Inputs(BaseInputs):
        message: str

    class TestNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class Workflow(BaseWorkflow[Inputs, BaseState]):
        graph = TestNode

        class Outputs(BaseWorkflow.Outputs):
            final_output = TestNode.Outputs.result

    mock_outputs = TestNode.Outputs(result="mocked_result")

    # AND a dataset with mocks
    dataset = [
        DatasetRow(
            label="test_with_mocks",
            inputs={"message": "test"},
            mocks=[mock_outputs],
        ),
    ]

    workflow_instance = Workflow()
    original_stream = workflow_instance.stream
    stream_mock = MagicMock(return_value=original_stream(inputs=Inputs(message="test")))
    mocker.patch.object(workflow_instance, "stream", stream_mock)

    # WHEN we run the sandbox with the DatasetRow containing mocks
    runner = WorkflowSandboxRunner(workflow=workflow_instance, dataset=dataset)
    runner.run()

    stream_mock.assert_called_once()
    call_kwargs = stream_mock.call_args.kwargs
    assert "node_output_mocks" in call_kwargs
    assert call_kwargs["node_output_mocks"] == [mock_outputs]
