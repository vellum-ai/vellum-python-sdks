from unittest.mock import ANY
from uuid import uuid4
from typing import Any, Iterator, List, cast

from vellum import (
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    FunctionCall,
    FunctionCallVellumValue,
    InitiatedExecutePromptEvent,
    PromptOutput,
    StreamingExecutePromptEvent,
    StringInputRequest,
    StringVellumValue,
)
from vellum.workflows.constants import LATEST_RELEASE_TAG, OMIT
from vellum.workflows.events.types import CodeResourceDefinition, WorkflowParentContext
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.basic_prompt_deployment.workflow import BasicPromptDeploymentWorkflow, Inputs


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
    assert terminal_event.outputs == {"results": expected_outputs, "text": "I'm looking up the weather for you now."}

    # AND we should have invoked the Prompt Deployment with the expected inputs
    vellum_client.execute_prompt_stream.assert_called_once_with(
        inputs=[
            StringInputRequest(name="city", type="STRING", value="San Francisco"),
            StringInputRequest(name="date", type="STRING", value="2024-01-01"),
        ],
        prompt_deployment_id=None,
        prompt_deployment_name="example_prompt_deployment",
        release_tag=LATEST_RELEASE_TAG,
        external_id=OMIT,
        expand_meta=OMIT,
        raw_overrides=OMIT,
        expand_raw=OMIT,
        metadata=OMIT,
        request_options=None,
        execution_context=ANY,
    )

    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    parent_context = call_kwargs["execution_context"].get("parent_context")
    assert parent_context["workflow_definition"] == CodeResourceDefinition.encode(workflow.__class__).model_dump()


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
