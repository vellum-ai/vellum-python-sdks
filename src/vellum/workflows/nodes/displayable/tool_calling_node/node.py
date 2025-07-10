from typing import ClassVar, Iterator, List, Optional, Set

from vellum import ChatMessage, PromptBlock
from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.workflow import is_workflow_event
from vellum.workflows.exceptions import NodeException
from vellum.workflows.graph.graph import Graph
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import (
    create_function_node,
    create_tool_router_node,
    get_function_name,
)
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.core import EntityInputsInterface, Tool
from vellum.workflows.workflows.event_filters import all_workflow_event_filter


class ToolCallingNode(BaseNode):
    """
    A Node that dynamically invokes the provided functions to the underlying Prompt

    Attributes:
        ml_model: str - The model to use for tool calling (e.g., "gpt-4o-mini")
        blocks: List[PromptBlock] - The prompt blocks to use (same format as InlinePromptNode)
        functions: List[Tool] - The functions that can be called
        prompt_inputs: Optional[EntityInputsInterface] - Mapping of input variable names to values
        max_prompt_iterations: Optional[int] - Maximum number of prompt iterations before stopping
    """

    ml_model: ClassVar[str] = "gpt-4o-mini"
    blocks: ClassVar[List[PromptBlock]] = []
    functions: ClassVar[List[Tool]] = []
    prompt_inputs: ClassVar[Optional[EntityInputsInterface]] = None
    max_prompt_iterations: ClassVar[Optional[int]] = 5

    class Outputs(BaseOutputs):
        """
        The outputs of the ToolCallingNode.

        text: The final text response after tool calling
        chat_history: The complete chat history including tool calls
        """

        text: str
        chat_history: List[ChatMessage]

    def run(self) -> Iterator[BaseOutput]:
        """
        Run the tool calling workflow with streaming support.

        This dynamically builds a graph with router and function nodes,
        then executes the workflow and streams chat_history updates.
        """

        self._build_graph()

        with execution_context(parent_context=get_parent_context()):

            class ToolCallingState(BaseState):
                chat_history: List[ChatMessage] = []
                prompt_iterations: int = 0

            from vellum.workflows.workflows.base import BaseWorkflow

            class ToolCallingWorkflow(BaseWorkflow[BaseInputs, ToolCallingState]):
                graph = self._graph

                class Outputs(BaseWorkflow.Outputs):
                    chat_history: List[ChatMessage] = ToolCallingState.chat_history
                    text: str = self.tool_router_node.Outputs.text

            subworkflow = ToolCallingWorkflow(
                parent_state=self.state,
                context=WorkflowContext.create_from(self._context),
            )

            subworkflow_stream = subworkflow.stream(
                event_filter=all_workflow_event_filter,
                node_output_mocks=self._context._get_all_node_output_mocks(),
            )

        outputs: Optional[BaseOutputs] = None
        exception: Optional[NodeException] = None
        fulfilled_output_names: Set[str] = set()
        streaming_outputs: dict[str, BaseOutput] = {}

        # Yield initiated event for chat_history
        yield BaseOutput(name="chat_history")

        for event in subworkflow_stream:
            self._context._emit_subworkflow_event(event)

            if not is_workflow_event(event):
                continue
            if event.workflow_definition != ToolCallingWorkflow:
                continue

            if event.name == "workflow.execution.streaming":
                if event.output.name in ["chat_history", "text"]:
                    if event.output.is_fulfilled:
                        fulfilled_output_names.add(event.output.name)

                    streaming_outputs[event.output.name] = event.output

                    chat_history_output = streaming_outputs.get("chat_history")
                    text_output = streaming_outputs.get("text")

                    if chat_history_output and chat_history_output.is_streaming:
                        yield chat_history_output
                        if text_output:
                            yield text_output
                        streaming_outputs.clear()
                    # If we have fulfilled outputs, prioritize text first
                    elif (
                        text_output
                        and text_output.is_fulfilled
                        and chat_history_output
                        and chat_history_output.is_fulfilled
                    ):
                        yield text_output
                        yield chat_history_output
                        streaming_outputs.clear()
                    elif len(streaming_outputs) == 1:
                        yield from streaming_outputs.values()
                        streaming_outputs.clear()
            elif event.name == "workflow.execution.fulfilled":
                outputs = event.outputs
            elif event.name == "workflow.execution.rejected":
                exception = NodeException.of(event.error)

        if exception:
            raise exception

        if outputs is None:
            raise NodeException(
                message="Expected to receive outputs from Tool Calling Workflow",
                code=WorkflowErrorCode.INVALID_OUTPUTS,
            )

        output_list = list(outputs)
        text_outputs = [
            (desc, val) for desc, val in output_list if desc.name == "text" and desc.name not in fulfilled_output_names
        ]
        chat_history_outputs = [
            (desc, val)
            for desc, val in output_list
            if desc.name == "chat_history" and desc.name not in fulfilled_output_names
        ]
        other_outputs = [
            (desc, val)
            for desc, val in output_list
            if desc.name not in ["text", "chat_history"] and desc.name not in fulfilled_output_names
        ]

        for output_descriptor, output_value in text_outputs + chat_history_outputs + other_outputs:
            yield BaseOutput(
                name=output_descriptor.name,
                value=output_value,
            )

    def _build_graph(self) -> None:
        self.tool_router_node = create_tool_router_node(
            ml_model=self.ml_model,
            blocks=self.blocks,
            functions=self.functions,
            prompt_inputs=self.prompt_inputs,
            max_prompt_iterations=self.max_prompt_iterations,
        )

        self._function_nodes = {}
        for function in self.functions:
            function_name = get_function_name(function)

            self._function_nodes[function_name] = create_function_node(
                function=function,
                tool_router_node=self.tool_router_node,
            )

        graph_set = set()

        # Add connections from ports of router to function nodes and back to router
        for function_name, FunctionNodeClass in self._function_nodes.items():
            router_port = getattr(self.tool_router_node.Ports, function_name)
            edge_graph = router_port >> FunctionNodeClass >> self.tool_router_node
            graph_set.add(edge_graph)

        default_port = getattr(self.tool_router_node.Ports, "default")
        graph_set.add(default_port)

        self._graph = Graph.from_set(graph_set)
