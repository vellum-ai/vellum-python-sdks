from unittest.mock import ANY
from uuid import uuid4
from typing import Any, Iterator, List

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
from vellum.workflows.constants import LATEST_RELEASE_TAG
from vellum.workflows.events.types import VellumCodeResourceDefinition

from tests.workflows.basic_text_prompt_deployment.workflow import (
    BasicTextPromptDeployment,
    ExamplePromptDeploymentNode,
    Inputs,
)


def test_run_workflow__happy_path(vellum_client):
    """Confirm that we can successfully invoke a Workflow with a single Prompt Deployment Node"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment
    workflow = BasicTextPromptDeployment()

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
    assert "I'm looking up the weather for you now." in terminal_event.outputs.text

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
        expand_meta=None,
        raw_overrides=None,
        expand_raw=None,
        metadata=None,
        request_options=ANY,
    )

    call_kwargs = vellum_client.execute_prompt_stream.call_args.kwargs
    parent_context = call_kwargs["request_options"]["additional_body_parameters"]["execution_context"].get(
        "parent_context"
    )
    assert parent_context["node_definition"] == VellumCodeResourceDefinition.encode(
        ExamplePromptDeploymentNode
    ).model_dump(mode="json")


def test_stream_workflow__happy_path(vellum_client):
    """Confirm that we can successfully stream a Workflow with a single Prompt Deployment Node"""

    # GIVEN a workflow that's set up to hit a Prompt Deployment
    workflow = BasicTextPromptDeployment()

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
    result = workflow.stream(
        inputs=Inputs(
            city="San Francisco",
            date="2024-01-01",
        )
    )
    events = list(result)

    # THEN the workflow should have completed successfully with 12 events
    assert len(events) == 12

    # AND the outputs should be as expected
    assert events[0].name == "workflow.execution.initiated"

    assert events[1].name == "workflow.execution.streaming"
    assert events[1].output.is_fulfilled
    assert events[1].output.name == "text"
    assert events[1].output.value == "It was hot"

    assert events[2].name == "workflow.execution.fulfilled"
    assert events[2].outputs == {
        "text": "It was hot",
    }
