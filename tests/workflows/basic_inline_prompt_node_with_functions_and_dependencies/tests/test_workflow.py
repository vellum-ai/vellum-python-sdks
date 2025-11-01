from unittest import mock
from uuid import uuid4
from typing import Any, Iterator, List

from vellum import (
    AdHocExpandMeta,
    ChatMessagePromptBlock,
    ExecutePromptEvent,
    FulfilledExecutePromptEvent,
    InitiatedExecutePromptEvent,
    JinjaPromptBlock,
    PromptOutput,
    PromptRequestStringInput,
    StringVellumValue,
    VellumVariable,
)
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.basic_inline_prompt_node_with_functions_and_dependencies.workflow import (
    BasicInlinePromptWithFunctionsWorkflow,
    WorkflowInputs,
)


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """Confirm that we can successfully invoke a Workflow with a single Inline Prompt Node that includes functions"""

    # GIVEN a workflow that's set up to hit a Prompt
    workflow = BasicInlinePromptWithFunctionsWorkflow()

    # AND we know what the Prompt will respond with
    expected_outputs: List[PromptOutput] = [
        StringVellumValue(value="Your favorite animal is a fox."),
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
                value="animal",
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
        functions=None,
        expand_meta=AdHocExpandMeta(cost=None, model_name=None, usage=None, finish_reason=True),
        request_options=mock.ANY,
        settings=None,
    )
