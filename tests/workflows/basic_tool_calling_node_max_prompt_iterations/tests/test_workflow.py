from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.basic_tool_calling_node_max_prompt_iterations.workflow import (
    BasicToolCallingNodeMaxPromptIterationsWorkflow,
)


def test_tool_calling_node_max_prompt_iterations_workflow(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Test that the BasicToolCallingNodeMaxPromptIterationsWorkflow respects the max_prompt_iterations=2 limit.
    """

    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:  # noqa: U100
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            # First call: LLM decides to call add_numbers
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"a": 5, "b": 3},
                        id="call_1",
                        name="add_numbers",
                        state="FULFILLED",
                    ),
                ),
            ]
        elif call_count == 2:
            # Second call: LLM tries to call multiply_numbers but is blocked by max_prompt_iterations
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"a": 8, "b": 2},
                        id="call_2",
                        name="multiply_numbers",
                        state="FULFILLED",
                    ),
                ),
            ]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    # Set up the mock to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    uuid4_generator()
    uuid4_generator()
    uuid4_generator()
    uuid4_generator()

    # GIVEN a limited tool calls workflow with max_tool_calls=2
    workflow = BasicToolCallingNodeMaxPromptIterationsWorkflow()

    # WHEN the workflow is executed
    terminal_event = workflow.run()

    # THEN the workflow is executed successfully
    assert terminal_event.name == "workflow.execution.rejected"

    assert vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count == 1

    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION
    assert terminal_event.error.message == "Maximum number of prompt iterations `1` reached."
