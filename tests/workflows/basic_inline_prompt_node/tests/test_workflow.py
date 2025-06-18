from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExecutePromptEvent,
    ChatMessagePromptBlock,
    FulfilledAdHocExecutePromptEvent,
    InitiatedAdHocExecutePromptEvent,
    JinjaPromptBlock,
    PromptOutput,
    PromptRequestStringInput,
    StreamingAdHocExecutePromptEvent,
    StringVellumValue,
    VellumVariable,
)
from vellum.client.types.prompt_settings import PromptSettings
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.basic_inline_prompt_node.workflow import BasicInlinePromptWorkflow, WorkflowInputs


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """Confirm that we can successfully invoke a Workflow with a single Inline Prompt Node"""

    # GIVEN a workflow that's set up to hit a Prompt
    workflow = BasicInlinePromptWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="I'm looking up the weather for you now."),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[AdHocExecutePromptEvent] = [
            InitiatedAdHocExecutePromptEvent(execution_id=execution_id),
            FulfilledAdHocExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    expected_input_variable_id = uuid4_generator()

    # WHEN we run the workflow
    terminal_event = workflow.run(inputs=WorkflowInputs(noun="color"))

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs == {
        "results": expected_outputs,
    }

    # AND we should have invoked the Prompt with the expected inputs
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.assert_called_once_with(
        ml_model="gpt-4o",
        input_values=[
            PromptRequestStringInput(
                key="noun",
                type="STRING",
                value="color",
            ),
        ],
        input_variables=[
            VellumVariable(
                id=str(expected_input_variable_id),
                key="noun",
                type="STRING",
            ),
        ],
        parameters=DEFAULT_PROMPT_PARAMETERS,
        blocks=[
            ChatMessagePromptBlock(
                chat_role="SYSTEM",
                blocks=[
                    JinjaPromptBlock(
                        block_type="JINJA",
                        template="What's your favorite {{noun}}?",
                    ),
                ],
            ),
        ],
        expand_meta=None,
        functions=None,
        request_options=mock.ANY,
        settings=PromptSettings(timeout=1, stream_enabled=True),
    )


def test_stream_workflow__happy_path(vellum_adhoc_prompt_client):
    """Confirm that we can successfully stream a Workflow with a single Inline Prompt Node"""

    # GIVEN a workflow that's set up to hit a Prompt
    workflow = BasicInlinePromptWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="It was hot"),
    ]

    def generate_prompt_events(*args: Any, **kwargs: Any) -> Iterator[AdHocExecutePromptEvent]:
        execution_id = str(uuid4())
        events: List[AdHocExecutePromptEvent] = [
            InitiatedAdHocExecutePromptEvent(execution_id=execution_id),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value="It"), output_index=0
            ),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value=" was"), output_index=0
            ),
            StreamingAdHocExecutePromptEvent(
                execution_id=execution_id, output=StringVellumValue(value=" hot"), output_index=0
            ),
            FulfilledAdHocExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the workflow
    result = workflow.stream(inputs=WorkflowInputs(noun="color"))
    events = list(result)

    # THEN the workflow should have completed successfully with 7 events
    assert len(events) == 7

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

    assert events[6].name == "workflow.execution.fulfilled"
    assert events[6].outputs == {
        "results": expected_outputs,
    }
