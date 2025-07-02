from typing import ClassVar, List, Optional

from vellum import ChatMessage, PromptBlock
from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.graph.graph import Graph
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import (
    create_function_node,
    create_tool_router_node,
    get_function_name,
)
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.core import EntityInputsInterface, Tool


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

    def run(self) -> Outputs:
        """
        Run the tool calling workflow.

        This dynamically builds a graph with router and function nodes,
        then executes the workflow.
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
                    text: str = self.tool_router_node.Outputs.text
                    chat_history: List[ChatMessage] = ToolCallingState.chat_history

            subworkflow = ToolCallingWorkflow(
                parent_state=self.state,
                context=WorkflowContext.create_from(self._context),
            )

            terminal_event = subworkflow.run()

            if terminal_event.name == "workflow.execution.paused":
                raise NodeException(
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                    message="Subworkflow unexpectedly paused",
                )
            elif terminal_event.name == "workflow.execution.fulfilled":
                node_outputs = self.Outputs(
                    text=terminal_event.outputs.text,
                    chat_history=terminal_event.outputs.chat_history,
                )

                return node_outputs
            elif terminal_event.name == "workflow.execution.rejected":
                raise NodeException(message=terminal_event.error.message, code=terminal_event.error.code)

            raise Exception(f"Unexpected workflow event: {terminal_event.name}")

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
