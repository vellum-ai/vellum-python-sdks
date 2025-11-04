from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExecutePromptEvent,
    AdHocExpandMeta,
    ChatMessagePromptBlock,
    FulfilledAdHocExecutePromptEvent,
    InitiatedAdHocExecutePromptEvent,
    JinjaPromptBlock,
    PromptOutput,
    PromptRequestStringInput,
    StringVellumValue,
    VellumVariable,
)
from vellum.client.types.prompt_settings import PromptSettings
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.prompt_node_with_base_node_inputs.workflow import PromptNodeWithBaseNodeInputsWorkflow


def test_run_workflow__prompt_node_with_base_node_inputs(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Tests that a prompt node correctly receives resolved values from base node outputs.
    """

    workflow = PromptNodeWithBaseNodeInputsWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="The best place for hiking near San Francisco is Muir Woods."),
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
    expected_city_input_variable_id = uuid4_generator()
    expected_activity_input_variable_id = uuid4_generator()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the outputs should be as expected
    assert terminal_event.outputs == {
        "results": expected_outputs,
    }

    # AND we should have invoked the Prompt with the correct resolved values from base nodes
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.assert_called_once()
    call_kwargs = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args.kwargs

    assert call_kwargs["input_values"] == [
        PromptRequestStringInput(
            key="city",
            type="STRING",
            value="San Francisco",
        ),
        PromptRequestStringInput(
            key="activity",
            type="STRING",
            value="hiking",
        ),
    ]

    assert call_kwargs["input_variables"] == [
        VellumVariable(
            id=str(expected_city_input_variable_id),
            key="city",
            type="STRING",
        ),
        VellumVariable(
            id=str(expected_activity_input_variable_id),
            key="activity",
            type="STRING",
        ),
    ]

    assert call_kwargs["ml_model"] == "gpt-4o"
    assert call_kwargs["parameters"] == DEFAULT_PROMPT_PARAMETERS
    assert call_kwargs["blocks"] == [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    block_type="JINJA",
                    template="What's the best place for {{activity}} near {{city}}?",
                ),
            ],
        ),
    ]
    assert call_kwargs["expand_meta"] == AdHocExpandMeta(cost=None, model_name=None, usage=None, finish_reason=True)
    assert call_kwargs["functions"] is None
    assert call_kwargs["settings"] == PromptSettings(timeout=1, stream_enabled=True)
