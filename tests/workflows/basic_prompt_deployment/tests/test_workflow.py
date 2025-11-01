from unittest.mock import ANY
from uuid import uuid4
from typing import Any, Iterator, List, cast

from vellum import (
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    FunctionCall,
    FunctionCallVellumValue,
    InitiatedExecutePromptEvent,
    PromptDeploymentExpandMetaRequest,
    PromptOutput,
    StreamingExecutePromptEvent,
    StringInputRequest,
    StringVellumValue,
)
from vellum.client.core.api_error import ApiError
from vellum.workflows.constants import LATEST_RELEASE_TAG
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.types import VellumCodeResourceDefinition, WorkflowParentContext
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.basic_prompt_deployment.workflow import (
    BasicPromptDeploymentWorkflow,
    ExamplePromptDeploymentNode,
    Inputs,
)
from tests.workflows.basic_prompt_deployment.workflow_with_optional_inputs import (
    InputsWithOptional,
    WorkflowWithOptionalInputs,
)


def test_run_workflow__happy_path(vellum_client):
    """Confirm that we can successfully invoke a Workflow with a single Prompt Deployment Node"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment
    workflow = BasicPromptDeploymentWorkflow()

    # AND we know what the Prompt Deployment will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="I'm looking up the weather for you now."),
        FunctionCallVellumValue(value=FunctionCall(name="get_current_weather", arguments={"city": "San Francisco"})),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the workflow
    terminal_event = workflow.run(
        inputs=Inputs(
            city="San Francisco",
            date="2024-01-01",
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs.results == expected_outputs

    # AND we should have invoked the Prompt Deployment with the expected inputs
    vellum_client.execute_prompt_stream.assert_called_once_with(
        inputs=[
            StringInputRequest(name="city", type="STRING", value="San Francisco"),
            StringInputRequest(name="date", type="STRING", value="2024-01-01"),
        ],
        prompt_deployment_id=None,
        prompt_deployment_name="example_prompt_deployment",
        release_tag=LATEST_RELEASE_TAG,
        external_id=None,
        expand_meta=PromptDeploymentExpandMetaRequest(
            model_name=None,
            usage=None,
            cost=None,
            finish_reason=True,
            latency=None,
            deployment_release_tag=None,
            prompt_version_id=None,
        ),
        raw_overrides=None,
        expand_raw=None,
        metadata=None,
        request_options=ANY,
    )

    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    parent_context = call_kwargs["request_options"]["additional_body_parameters"]["execution_context"].get(
        "parent_context"
    )
    trace_id = call_kwargs["request_options"]["additional_body_parameters"]["execution_context"]["trace_id"]
    assert trace_id is not None
    assert parent_context["node_definition"] == VellumCodeResourceDefinition.encode(
        ExamplePromptDeploymentNode
    ).model_dump(mode="json")


def test_run_workflow_return_only_function_call__happy_path(vellum_client):
    """Confirm that we can successfully invoke a Workflow with a single Prompt Deployment Node"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment
    workflow = BasicPromptDeploymentWorkflow()

    # AND we know what the Prompt Deployment will respond with ONLY function call outputs
    expected_outputs: List[PromptOutput] = [
        FunctionCallVellumValue(value=FunctionCall(name="get_current_weather", arguments={"city": "San Francisco"})),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the workflow
    terminal_event = workflow.run(
        inputs=Inputs(
            city="San Francisco",
            date="2024-01-01",
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs.results == expected_outputs

    # AND we should have invoked the Prompt Deployment with the expected inputs
    vellum_client.execute_prompt_stream.assert_called_once_with(
        inputs=[
            StringInputRequest(name="city", type="STRING", value="San Francisco"),
            StringInputRequest(name="date", type="STRING", value="2024-01-01"),
        ],
        prompt_deployment_id=None,
        prompt_deployment_name="example_prompt_deployment",
        release_tag=LATEST_RELEASE_TAG,
        external_id=None,
        expand_meta=PromptDeploymentExpandMetaRequest(
            model_name=None,
            usage=None,
            cost=None,
            finish_reason=True,
            latency=None,
            deployment_release_tag=None,
            prompt_version_id=None,
        ),
        raw_overrides=None,
        expand_raw=None,
        metadata=None,
        request_options=ANY,
    )

    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    parent_context = call_kwargs["request_options"]["additional_body_parameters"]["execution_context"].get(
        "parent_context"
    )
    assert call_kwargs["request_options"]["additional_body_parameters"]["execution_context"]["trace_id"] is not None
    assert parent_context["node_definition"] == VellumCodeResourceDefinition.encode(
        ExamplePromptDeploymentNode
    ).model_dump(mode="json")


def test_stream_workflow__happy_path(vellum_client):
    """Confirm that we can successfully stream a Workflow with a single Prompt Deployment Node"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment
    workflow = BasicPromptDeploymentWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="It was hot"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            StreamingExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value="It"), output_index=0
            ),
            StreamingExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value=" was"), output_index=0
            ),
            StreamingExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value=" hot"), output_index=0
            ),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

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

    assert events[1].name == "workflow.execution.streaming"
    assert events[1].output.is_initiated
    assert events[1].output.name == "results"

    assert events[2].name == "workflow.execution.streaming"
    assert events[2].output.is_streaming
    assert events[2].output.name == "results"
    assert events[2].output.delta == "It"

    assert events[3].name == "workflow.execution.streaming"
    assert events[3].output.is_streaming
    assert events[3].output.name == "results"
    assert events[3].output.delta == " was"

    assert events[4].name == "workflow.execution.streaming"
    assert events[4].output.is_streaming
    assert events[4].output.name == "results"
    assert events[4].output.delta == " hot"

    assert events[5].name == "workflow.execution.streaming"
    assert events[5].output.is_fulfilled
    assert events[5].output.name == "results"
    assert events[5].output.value == expected_outputs

    assert events[6].name == "workflow.execution.streaming"
    assert events[6].output.is_fulfilled
    assert events[6].output.name == "text"
    assert events[6].output.value == "It was hot"

    assert events[7].name == "workflow.execution.fulfilled"
    assert events[7].outputs == {
        "results": expected_outputs,
        "text": "It was hot",
    }

    assert node_events[0].name == "node.execution.initiated"
    assert (
        cast(WorkflowParentContext, node_events[0].parent).workflow_definition.model_dump()
        == WorkflowParentContext(
            workflow_definition=workflow.__class__, span_id=uuid4()
        ).workflow_definition.model_dump()
    )


def test_stream_workflow__deployment_not_found(vellum_client):
    """Confirm that we emit the correct events when a deployment is not found"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment
    workflow = BasicPromptDeploymentWorkflow()

    # AND the Prompt Deployment is not found
    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        if kwargs.get("_mock_condition_to_induce_an_error"):
            yield InitiatedExecutePromptEvent(execution_id=str(uuid4()))
        else:
            raise ApiError(status_code=404, body={"detail": "Deployment not found"})

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

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

    events = next(
        event
        for event in result
        if event.name == "workflow.execution.rejected" or event.name == "workflow.execution.fulfilled"
    )

    # THEN the last event should be a rejected event
    assert events.name == "workflow.execution.rejected"
    assert events.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert events.error.message == "Deployment not found"


def test_run_workflow__optional_inputs_excluded(vellum_client):
    """Confirm that optional inputs with None values are excluded from the request"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment with optional inputs
    workflow = WorkflowWithOptionalInputs()

    # AND we know what the Prompt Deployment will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="I'm looking up the weather for you now."),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_client.execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the workflow without providing the optional field
    terminal_event = workflow.run(
        inputs=InputsWithOptional(
            city="San Francisco",
            date="2024-01-01",
        )
    )

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND we should have invoked the Prompt Deployment with only the required inputs
    vellum_client.execute_prompt_stream.assert_called_once_with(
        inputs=[
            StringInputRequest(name="city", type="STRING", value="San Francisco"),
            StringInputRequest(name="date", type="STRING", value="2024-01-01"),
        ],
        prompt_deployment_id=None,
        prompt_deployment_name="example_prompt_deployment_with_optional",
        release_tag=LATEST_RELEASE_TAG,
        external_id=None,
        expand_meta=PromptDeploymentExpandMetaRequest(
            model_name=None,
            usage=None,
            cost=None,
            finish_reason=True,
            latency=None,
            deployment_release_tag=None,
            prompt_version_id=None,
        ),
        raw_overrides=None,
        expand_raw=None,
        metadata=None,
        request_options=ANY,
    )

    # AND the optional input should not be present in the request
    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    input_names = [input_req.name for input_req in call_kwargs["inputs"]]
    assert "optional_field" not in input_names
    assert len(call_kwargs["inputs"]) == 2
