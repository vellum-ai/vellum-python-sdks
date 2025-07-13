import json
from typing import Any, Iterator, List, Optional, Type, cast

from pydash import snake_case

from vellum import ChatMessage, PromptBlock
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.workflow import is_workflow_event
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior, Tool
from vellum.workflows.types.definition import DeploymentDefinition
from vellum.workflows.types.generics import is_workflow_class
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

CHAT_HISTORY_VARIABLE = "chat_history"


class FunctionNode(BaseNode):
    """Node that executes a specific function."""

    pass


class ToolRouterNode(InlinePromptNode[ToolCallingState]):
    max_prompt_iterations: Optional[int] = 5

    class Trigger(InlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES

    def run(self) -> Iterator[BaseOutput]:
        if self.state.prompt_iterations >= self.max_prompt_iterations:
            max_iterations_message = f"Maximum number of prompt iterations `{self.max_prompt_iterations}` reached."
            raise NodeException(message=max_iterations_message, code=WorkflowErrorCode.NODE_EXECUTION)

        # Merge user-provided chat history with node's chat history
        user_chat_history = self.prompt_inputs.get(CHAT_HISTORY_VARIABLE, []) if self.prompt_inputs else []
        merged_chat_history = user_chat_history + self.state.chat_history
        self.prompt_inputs = {**self.prompt_inputs, CHAT_HISTORY_VARIABLE: merged_chat_history}  # type: ignore
        generator = super().run()
        for output in generator:
            if output.name == "results" and output.value:
                values = cast(List[Any], output.value)
                if values and len(values) > 0:
                    if values[0].type == "STRING":
                        self.state.chat_history.append(ChatMessage(role="ASSISTANT", text=values[0].value))
                    elif values[0].type == "FUNCTION_CALL":
                        self.state.prompt_iterations += 1

                        function_call = values[0].value
                        if function_call is not None:
                            self.state.chat_history.append(
                                ChatMessage(
                                    role="ASSISTANT",
                                    content=FunctionCallChatMessageContent(
                                        value=FunctionCallChatMessageContentValue(
                                            name=function_call.name,
                                            arguments=function_call.arguments,
                                            id=function_call.id,
                                        ),
                                    ),
                                )
                            )
            yield output


class DynamicSubworkflowDeploymentNode(SubworkflowDeploymentNode[ToolCallingState]):
    """Node that executes a deployment definition with function call output."""

    function_call_output: List[PromptOutput]

    def run(self) -> Iterator[BaseOutput]:
        if self.function_call_output and len(self.function_call_output) > 0:
            function_call = self.function_call_output[0]
            if function_call.type == "FUNCTION_CALL" and function_call.value is not None:
                arguments = function_call.value.arguments
            else:
                arguments = {}
        else:
            arguments = {}

        # Mypy doesn't like instance assignments of class attributes. It's safe in our case tho bc it's what
        # we do in the `__init__` method. Long term, instead of the function_call_output attribute above, we
        # want to do:
        # ```python
        # subworkflow_inputs = tool_router_node.Outputs.results[0]['value']['arguments'].if_(
        #     tool_router_node.Outputs.results[0]['type'].equals('FUNCTION_CALL'),
        #     {},
        # )
        # ```
        self.subworkflow_inputs = arguments  # type:ignore[misc]

        # Call the parent run method to execute the subworkflow
        outputs = {}
        for output in super().run():
            if output.is_fulfilled:
                outputs[output.name] = output.value
            yield output

        # Add the result to the chat history
        self.state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(outputs, cls=DefaultStateEncoder)),
            )
        )


def create_tool_router_node(
    ml_model: str,
    blocks: List[PromptBlock],
    functions: List[Tool],
    prompt_inputs: Optional[EntityInputsInterface],
    max_prompt_iterations: Optional[int] = None,
) -> Type[ToolRouterNode]:
    if functions and len(functions) > 0:
        # If we have functions, create dynamic ports for each function
        Ports = type("Ports", (), {})
        for function in functions:
            function_name = get_function_name(function)

            # Avoid using lambda to capture function_name
            # lambda will capture the function_name by reference,
            # and if the function_name is changed, the port_condition will also change.
            def create_port_condition(fn_name):
                return LazyReference(
                    lambda: (
                        node.Outputs.results[0]["type"].equals("FUNCTION_CALL")
                        & node.Outputs.results[0]["value"]["name"].equals(fn_name)
                    )
                )

            port_condition = create_port_condition(function_name)
            port = Port.on_if(port_condition)
            setattr(Ports, function_name, port)

        # Add the else port for when no function conditions match
        setattr(Ports, "default", Port.on_else())
    else:
        # If no functions exist, create a simple Ports class with just a default port
        Ports = type("Ports", (), {"default": Port(default=True)})

    # Add a chat history block to blocks only if one doesn't already exist
    has_chat_history_block = any(
        block.block_type == "VARIABLE" and block.input_variable == CHAT_HISTORY_VARIABLE for block in blocks
    )

    if not has_chat_history_block:
        blocks.append(
            VariablePromptBlock(
                block_type="VARIABLE",
                input_variable=CHAT_HISTORY_VARIABLE,
                state=None,
                cache_config=None,
            )
        )

    node = cast(
        Type[ToolRouterNode],
        type(
            "ToolRouterNode",
            (ToolRouterNode,),
            {
                "ml_model": ml_model,
                "blocks": blocks,
                "functions": functions,
                "prompt_inputs": prompt_inputs,
                "max_prompt_iterations": max_prompt_iterations,
                "Ports": Ports,
                "__module__": __name__,
            },
        ),
    )
    return node


def create_function_node(
    function: Tool,
    tool_router_node: Type[ToolRouterNode],
) -> Type[FunctionNode]:
    """
    Create a FunctionNode class for a given function.

    For workflow functions: BaseNode
    For regular functions: BaseNode with direct function call

    Args:
        function: The function to create a node for
        tool_router_node: The tool router node class
    """
    if isinstance(function, DeploymentDefinition):
        deployment = function.deployment_id or function.deployment_name
        release_tag = function.release_tag

        node = type(
            f"DynamicSubworkflowDeploymentNode_{deployment}",
            (DynamicSubworkflowDeploymentNode,),
            {
                "deployment": deployment,
                "release_tag": release_tag,
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )

        return node

    elif is_workflow_class(function):
        # Create a class-level wrapper that calls the original function
        def execute_inline_workflow_function(self) -> BaseNode.Outputs:
            function_call_output = self.state.meta.node_outputs.get(tool_router_node.Outputs.results)
            if function_call_output and len(function_call_output) > 0:
                function_call = function_call_output[0]
                arguments = function_call.value.arguments
            else:
                arguments = {}

            # Call the function based on its type
            inputs_instance = function.get_inputs_class()(**arguments)

            with execution_context(parent_context=get_parent_context()):
                workflow = function(
                    parent_state=self.state,
                    context=WorkflowContext.create_from(self._context),
                )
                subworkflow_stream = workflow.stream(
                    inputs=inputs_instance,
                    event_filter=all_workflow_event_filter,
                    node_output_mocks=self._context._get_all_node_output_mocks(),
                )

            outputs: Optional[BaseOutputs] = None
            exception: Optional[NodeException] = None

            for event in subworkflow_stream:
                self._context._emit_subworkflow_event(event)
                if exception:
                    continue

                if not is_workflow_event(event):
                    continue
                if event.workflow_definition != function:
                    continue

                if event.name == "workflow.execution.fulfilled":
                    outputs = event.outputs
                elif event.name == "workflow.execution.rejected":
                    exception = NodeException.of(event.error)
                elif event.name == "workflow.execution.paused":
                    exception = NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message="Subworkflow unexpectedly paused",
                    )

            if exception:
                raise exception

            if outputs is None:
                raise NodeException(
                    message="Expected to receive outputs from inline subworkflow",
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                )

            result = outputs

            self.state.chat_history.append(
                ChatMessage(
                    role="FUNCTION",
                    content=StringChatMessageContent(value=json.dumps(result, cls=DefaultStateEncoder)),
                )
            )

            return self.Outputs()

        # Create BaseNode for workflow functions
        node = type(
            f"InlineWorkflowNode_{function.__name__}",
            (FunctionNode,),
            {
                "run": execute_inline_workflow_function,
                "__module__": __name__,
            },
        )
    else:
        # For regular functions, call them directly
        def execute_regular_function(self) -> BaseNode.Outputs:
            # Get the function call from the tool router output
            function_call_output = self.state.meta.node_outputs.get(tool_router_node.Outputs.results)
            if function_call_output and len(function_call_output) > 0:
                function_call = function_call_output[0]
                arguments = function_call.value.arguments
            else:
                arguments = {}

            # Call the function directly
            try:
                result = function(**arguments)
            except Exception as e:
                raise NodeException(
                    message=f"Error executing function '{function.__name__}': {str(e)}",
                    code=WorkflowErrorCode.NODE_EXECUTION,
                )

            # Add the result to the chat history
            self.state.chat_history.append(
                ChatMessage(
                    role="FUNCTION",
                    content=StringChatMessageContent(value=json.dumps(result, cls=DefaultStateEncoder)),
                )
            )

            return self.Outputs()

        # Create BaseNode for regular functions
        node = type(
            f"FunctionNode_{function.__name__}",
            (FunctionNode,),
            {
                "run": execute_regular_function,
                "__module__": __name__,
            },
        )

    return node


def get_function_name(function: Tool) -> str:
    if isinstance(function, DeploymentDefinition):
        name = str(function.deployment_id or function.deployment_name)
        return name.replace("-", "")
    else:
        return snake_case(function.__name__)
