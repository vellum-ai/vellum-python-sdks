import json
from uuid import uuid4
from typing import Callable, ClassVar, Generic, Iterator, List, Optional, Set, Tuple, Union

from vellum import (
    AdHocExecutePromptEvent,
    AdHocExpandMeta,
    ChatMessage,
    FunctionDefinition,
    PromptBlock,
    PromptParameters,
    PromptRequestChatHistoryInput,
    PromptRequestInput,
    PromptRequestJsonInput,
    PromptRequestStringInput,
    VellumVariable,
)
from vellum.client import RequestOptions
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.prompt_settings import PromptSettings
from vellum.client.types.rich_text_child_block import RichTextChildBlock
from vellum.workflows.constants import OMIT
from vellum.workflows.context import get_execution_context
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.events.types import default_serializer
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases.base_prompt_node import BasePromptNode
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType
from vellum.workflows.utils.functions import compile_function_definition


class BaseInlinePromptNode(BasePromptNode[StateType], Generic[StateType]):
    """
    Used to execute a Prompt defined inline.

    prompt_inputs: EntityInputsInterface - The inputs for the Prompt
    ml_model: str - Either the ML Model's UUID or its name.
    blocks: List[PromptBlock] - The blocks that make up the Prompt
    functions: Optional[List[FunctionDefinition]] - The functions to include in the Prompt
    parameters: PromptParameters - The parameters for the Prompt
    expand_meta: Optional[AdHocExpandMeta] - Expandable execution fields to include in the response
    request_options: Optional[RequestOptions] - The request options to use for the Prompt Execution
    """

    ml_model: ClassVar[str]

    # The blocks that make up the Prompt
    blocks: ClassVar[List[PromptBlock]]

    # The functions/tools that a Prompt has access to
    functions: Optional[List[Union[FunctionDefinition, Callable]]] = None

    parameters: PromptParameters = DEFAULT_PROMPT_PARAMETERS
    expand_meta: Optional[AdHocExpandMeta] = OMIT

    settings: Optional[PromptSettings] = None

    class Trigger(BasePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    def _extract_required_input_variables(self, blocks: Union[List[PromptBlock], List[RichTextChildBlock]]) -> Set[str]:
        required_variables = set()

        for block in blocks:
            if block.block_type == "VARIABLE":
                required_variables.add(block.input_variable)
            elif block.block_type == "CHAT_MESSAGE" and block.blocks:
                required_variables.update(self._extract_required_input_variables(block.blocks))
            elif block.block_type == "RICH_TEXT" and block.blocks:
                required_variables.update(self._extract_required_input_variables(block.blocks))

        return required_variables

    def _validate(self) -> None:
        required_variables = self._extract_required_input_variables(self.blocks)
        provided_variables = set(self.prompt_inputs.keys() if self.prompt_inputs else set())

        missing_variables = required_variables - provided_variables
        if missing_variables:
            missing_vars_str = ", ".join(f"'{var}'" for var in missing_variables)
            raise NodeException(
                message=f"Missing required input variables by VariablePromptBlock: {missing_vars_str}",
                code=WorkflowErrorCode.INVALID_INPUTS,
            )

    def _get_prompt_event_stream(self) -> Iterator[AdHocExecutePromptEvent]:
        input_variables, input_values = self._compile_prompt_inputs()
        execution_context = get_execution_context()
        request_options = self.request_options or RequestOptions()

        request_options["additional_body_parameters"] = {
            "execution_context": execution_context.model_dump(mode="json"),
            **request_options.get("additional_body_parameters", {}),
        }
        normalized_functions = (
            [
                function if isinstance(function, FunctionDefinition) else compile_function_definition(function)
                for function in self.functions
            ]
            if self.functions
            else None
        )

        return self._context.vellum_client.ad_hoc.adhoc_execute_prompt_stream(
            ml_model=self.ml_model,
            input_values=input_values,
            input_variables=input_variables,
            parameters=self.parameters,
            blocks=self.blocks,
            settings=self.settings,
            functions=normalized_functions,
            expand_meta=self.expand_meta,
            request_options=request_options,
        )

    def _compile_prompt_inputs(self) -> Tuple[List[VellumVariable], List[PromptRequestInput]]:
        input_variables: List[VellumVariable] = []
        input_values: List[PromptRequestInput] = []

        if not self.prompt_inputs:
            return input_variables, input_values

        for input_name, input_value in self.prompt_inputs.items():
            if isinstance(input_value, str):
                input_variables.append(
                    VellumVariable(
                        # TODO: Determine whether or not we actually need an id here and if we do,
                        #   figure out how to maintain stable id references.
                        #   https://app.shortcut.com/vellum/story/4080
                        id=str(uuid4()),
                        key=input_name,
                        type="STRING",
                    )
                )
                input_values.append(
                    PromptRequestStringInput(
                        key=input_name,
                        value=input_value,
                    )
                )
            elif (
                input_value
                and isinstance(input_value, list)
                and all(isinstance(message, (ChatMessage, ChatMessageRequest)) for message in input_value)
            ):
                chat_history = [
                    message if isinstance(message, ChatMessage) else ChatMessage.model_validate(message.model_dump())
                    for message in input_value
                    if isinstance(message, (ChatMessage, ChatMessageRequest))
                ]
                input_variables.append(
                    VellumVariable(
                        # TODO: Determine whether or not we actually need an id here and if we do,
                        #   figure out how to maintain stable id references.
                        #   https://app.shortcut.com/vellum/story/4080
                        id=str(uuid4()),
                        key=input_name,
                        type="CHAT_HISTORY",
                    )
                )
                input_values.append(
                    PromptRequestChatHistoryInput(
                        key=input_name,
                        value=chat_history,
                    )
                )
            else:
                try:
                    input_value = default_serializer(input_value)
                except json.JSONDecodeError as e:
                    raise NodeException(
                        message=f"Failed to serialize input '{input_name}' of type '{input_value.__class__}': {e}",
                        code=WorkflowErrorCode.INVALID_INPUTS,
                    )

                input_variables.append(
                    VellumVariable(
                        # TODO: Determine whether or not we actually need an id here and if we do,
                        #   figure out how to maintain stable id references.
                        #   https://app.shortcut.com/vellum/story/4080
                        id=str(uuid4()),
                        key=input_name,
                        type="JSON",
                    )
                )
                input_values.append(
                    PromptRequestJsonInput(
                        key=input_name,
                        value=input_value,
                    )
                )

        return input_variables, input_values
