from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.workflows.base import BaseWorkflow


def test_run_workflow__tool_with_workflow_context_parameter__receives_parent_context_data(vellum_adhoc_prompt_client):
    """
    Tests that the WorkflowContext passed to a function contains the parent workflow's context data.
    """
    # GIVEN a variable to capture the context passed to the function
    captured_context: List[WorkflowContext] = []

    # AND a function with a WorkflowContext parameter that captures the context
    def my_tool_with_context(ctx: WorkflowContext, query: str) -> str:
        captured_context.append(ctx)
        return f"Processed: {query}"

    # AND a workflow with a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = []
        functions = [my_tool_with_context]
        prompt_inputs = {}

    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # AND a mock that returns a function call followed by a text response
    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"query": "test query"},
                        id="call_123",
                        name="my_tool_with_context",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [StringVellumValue(value="Final response")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the workflow
    workflow = TestWorkflow()
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the function should have been called with a WorkflowContext
    assert len(captured_context) == 1
    assert isinstance(captured_context[0], WorkflowContext)
