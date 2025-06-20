import pytest
from datetime import datetime
from unittest.mock import ANY
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    WorkflowExecutionWorkflowResultEvent,
    WorkflowOutput,
    WorkflowOutputNumber,
    WorkflowOutputString,
    WorkflowRequestStringInputRequest,
    WorkflowResultEvent,
    WorkflowResultEventOutputDataNumber,
    WorkflowResultEventOutputDataString,
    WorkflowStreamEvent,
)
from vellum.workflows.constants import LATEST_RELEASE_TAG, OMIT
from vellum.workflows.events.types import VellumCodeResourceDefinition, WorkflowParentContext
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.basic_subworkflow_deployment.workflow import (
    BasicSubworkflowDeploymentWorkflow,
    ExampleSubworkflowDeploymentNode,
    Inputs,
)
from tests.workflows.basic_subworkflow_deployment.workflow_with_base_inputs import (
    TestInputs,
    WorkflowWithBaseInputsSubworkflow,
)
from tests.workflows.basic_subworkflow_deployment.workflow_with_optional_inputs import (
    InputsWithOptional,
    WorkflowWithOptionalInputsSubworkflow,
)


@pytest.mark.parametrize(
    "workflow_class,inputs_class",
    [
        (BasicSubworkflowDeploymentWorkflow, Inputs),
        (WorkflowWithBaseInputsSubworkflow, TestInputs),
    ],
)
def test_run_workflow__happy_path(vellum_client, workflow_class, inputs_class):
    """Confirm that we can successfully invoke a Workflow with a single Subworkflow Deployment Node"""

    # GIVEN a workflow that's set up to hit a Subworkflow Deployment
    workflow = workflow_class()

    # AND we know what the Workflow Deployment will respond with
    expected_outputs: List[WorkflowOutput] = [
        WorkflowOutputNumber(id=str(uuid4()), value=70, name="temperature"),
        WorkflowOutputString(
            id=str(uuid4()), value="I went to weather.com and looked at today's forecast.", name="reasoning"
        ),
    ]

    execution_id = str(uuid4())
    expected_events: List[WorkflowStreamEvent] = [
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="INITIATED",
                ts=datetime.now(),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="FULFILLED",
                ts=datetime.now(),
                outputs=expected_outputs,
            ),
        ),
    ]

    def generate_subworkflow_events(*args: Any, **kwargs: Any) -> Iterator[WorkflowStreamEvent]:
        yield from expected_events

    vellum_client.execute_workflow_stream.side_effect = generate_subworkflow_events

    # WHEN we run the workflow
    terminal_event = workflow.run(
        inputs=inputs_class(
            city="San Francisco",
            date="2024-01-01",
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs == {
        "temperature": 70,
        "reasoning": "I went to weather.com and looked at today's forecast.",
    }

    # AND we should have invoked the Workflow Deployment with the expected inputs
    vellum_client.execute_workflow_stream.assert_called_once_with(
        inputs=[
            WorkflowRequestStringInputRequest(name="city", type="STRING", value="San Francisco"),
            WorkflowRequestStringInputRequest(name="date", type="STRING", value="2024-01-01"),
        ],
        workflow_deployment_id=None,
        workflow_deployment_name="example_workflow_deployment",
        event_types=["WORKFLOW"],
        release_tag=LATEST_RELEASE_TAG,
        external_id=OMIT,
        metadata=OMIT,
        request_options=ANY,
    )

    call_args = vellum_client.execute_workflow_stream.call_args.kwargs
    parent_context = call_args["request_options"]["additional_body_parameters"]["execution_context"]["parent_context"]
    expected_context = VellumCodeResourceDefinition.encode(ExampleSubworkflowDeploymentNode).model_dump()
    assert parent_context["node_definition"]["id"] == str(expected_context["id"])
    assert parent_context["node_definition"]["module"] == expected_context["module"]
    assert parent_context["node_definition"]["name"] == expected_context["name"]


def test_stream_workflow__happy_path(vellum_client):
    """Confirm that we can successfully invoke a Workflow with a single Subworkflow Deployment Node"""

    # GIVEN a workflow that's set up to hit a Subworkflow Deployment
    workflow = BasicSubworkflowDeploymentWorkflow()

    # AND we know what the Workflow Deployment will respond with
    temperature_output_id = str(uuid4())
    temperature_node_id = str(uuid4())
    reasoning_output_id = str(uuid4())
    reasoning_node_id = str(uuid4())
    expected_outputs: List[WorkflowOutput] = [
        WorkflowOutputNumber(id=temperature_output_id, value=70, name="temperature"),
        WorkflowOutputString(id=reasoning_output_id, value="Went to weather.com", name="reasoning"),
    ]

    execution_id = str(uuid4())
    expected_events: List[WorkflowStreamEvent] = [
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="INITIATED",
                ts=datetime.now(),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="STREAMING",
                ts=datetime.now(),
                output=WorkflowResultEventOutputDataString(
                    id=reasoning_output_id,
                    name="reasoning",
                    state="INITIATED",
                    node_id=reasoning_node_id,
                    delta=None,
                    value=None,
                ),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="STREAMING",
                ts=datetime.now(),
                output=WorkflowResultEventOutputDataString(
                    id=reasoning_output_id,
                    name="reasoning",
                    state="STREAMING",
                    node_id=reasoning_node_id,
                    delta="Went",
                    value=None,
                ),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="STREAMING",
                ts=datetime.now(),
                output=WorkflowResultEventOutputDataString(
                    id=reasoning_output_id,
                    name="reasoning",
                    state="STREAMING",
                    node_id=reasoning_node_id,
                    delta=" to",
                    value=None,
                ),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="STREAMING",
                ts=datetime.now(),
                output=WorkflowResultEventOutputDataString(
                    id=reasoning_output_id,
                    name="reasoning",
                    state="STREAMING",
                    node_id=reasoning_node_id,
                    delta=" weather.com",
                    value=None,
                ),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="STREAMING",
                ts=datetime.now(),
                output=WorkflowResultEventOutputDataString(
                    id=reasoning_output_id,
                    name="reasoning",
                    state="FULFILLED",
                    node_id=reasoning_node_id,
                    delta=None,
                    value="Went to weather.com",
                ),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="STREAMING",
                ts=datetime.now(),
                output=WorkflowResultEventOutputDataNumber(
                    id=temperature_output_id,
                    name="temperature",
                    state="FULFILLED",
                    node_id=temperature_node_id,
                    delta=None,
                    value=70,
                ),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="FULFILLED",
                ts=datetime.now(),
                outputs=expected_outputs,
            ),
        ),
    ]

    def generate_subworkflow_events(*args: Any, **kwargs: Any) -> Iterator[WorkflowStreamEvent]:
        yield from expected_events

    vellum_client.execute_workflow_stream.side_effect = generate_subworkflow_events

    # WHEN we run the workflow
    result = list(
        workflow.stream(
            event_filter=root_workflow_event_filter,
            inputs=Inputs(
                city="San Francisco",
                date="2024-01-01",
            ),
        )
    )
    events = list(event for event in result if event.name.startswith("workflow."))
    node_events = list(event for event in result if event.name.startswith("node."))

    # THEN the workflow should have completed successfully with 8 events
    assert len(events) == 8

    # AND the outputs should be as expected
    assert events[0].name == "workflow.execution.initiated"
    assert events[0].parent is None

    assert events[1].name == "workflow.execution.streaming"
    assert events[1].output.is_initiated

    assert events[2].name == "workflow.execution.streaming"
    assert events[2].output.is_streaming
    assert events[2].output.name == "reasoning"
    assert events[2].output.delta == "Went"

    assert events[3].name == "workflow.execution.streaming"
    assert events[3].output.is_streaming
    assert events[3].output.name == "reasoning"
    assert events[3].output.delta == " to"

    assert events[4].name == "workflow.execution.streaming"
    assert events[4].output.is_streaming
    assert events[4].output.name == "reasoning"
    assert events[4].output.delta == " weather.com"

    assert events[5].name == "workflow.execution.streaming"
    assert events[5].output.is_fulfilled
    assert events[5].output.name == "reasoning"
    assert events[5].output.value == "Went to weather.com"

    assert events[6].name == "workflow.execution.streaming"
    assert events[6].output.is_fulfilled
    assert events[6].output.name == "temperature"
    assert events[6].output.value == 70

    assert events[7].name == "workflow.execution.fulfilled"
    assert events[7].outputs == {
        "temperature": 70,
        "reasoning": "Went to weather.com",
    }

    assert node_events[0].name == "node.execution.initiated"
    assert isinstance(node_events[0].parent, WorkflowParentContext)
    assert (
        node_events[0].parent.workflow_definition.model_dump()
        == WorkflowParentContext(
            workflow_definition=workflow.__class__, span_id=uuid4()
        ).workflow_definition.model_dump()
    )


def test_run_workflow__optional_inputs_excluded(vellum_client):
    """Confirm that optional inputs with None values are excluded from the request"""

    # GIVEN a workflow that's set up to hit a Subworkflow Deployment with optional inputs
    workflow = WorkflowWithOptionalInputsSubworkflow()

    # AND we know what the Workflow Deployment will respond with
    expected_outputs: List[WorkflowOutput] = [
        WorkflowOutputNumber(id=str(uuid4()), value=70, name="temperature"),
        WorkflowOutputString(
            id=str(uuid4()), value="I went to weather.com and looked at today's forecast.", name="reasoning"
        ),
    ]

    execution_id = str(uuid4())
    expected_events: List[WorkflowStreamEvent] = [
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="INITIATED",
                ts=datetime.now(),
            ),
        ),
        WorkflowExecutionWorkflowResultEvent(
            execution_id=execution_id,
            data=WorkflowResultEvent(
                id=str(uuid4()),
                state="FULFILLED",
                ts=datetime.now(),
                outputs=expected_outputs,
            ),
        ),
    ]

    def generate_subworkflow_events(*args: Any, **kwargs: Any) -> Iterator[WorkflowStreamEvent]:
        yield from expected_events

    vellum_client.execute_workflow_stream.side_effect = generate_subworkflow_events

    # WHEN we run the workflow without providing the optional field
    terminal_event = workflow.run(
        inputs=InputsWithOptional(
            city="San Francisco",
            date="2024-01-01",
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs == {
        "temperature": 70,
        "reasoning": "I went to weather.com and looked at today's forecast.",
    }

    # AND we should have invoked the Workflow Deployment with only the required inputs
    vellum_client.execute_workflow_stream.assert_called_once_with(
        inputs=[
            WorkflowRequestStringInputRequest(name="city", type="STRING", value="San Francisco"),
            WorkflowRequestStringInputRequest(name="date", type="STRING", value="2024-01-01"),
        ],
        workflow_deployment_id=None,
        workflow_deployment_name="example_subworkflow_deployment_with_optional",
        event_types=["WORKFLOW"],
        release_tag=LATEST_RELEASE_TAG,
        external_id=OMIT,
        metadata=OMIT,
        request_options=ANY,
    )

    # AND the optional input should not be present in the request
    call_kwargs = vellum_client.execute_workflow_stream.call_args.kwargs
    input_names = [input_req.name for input_req in call_kwargs["inputs"]]
    assert "optional_field" not in input_names
    assert len(call_kwargs["inputs"]) == 2
