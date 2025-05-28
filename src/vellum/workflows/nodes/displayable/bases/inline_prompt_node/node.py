import json
from uuid import uuid4
from typing import Callable, ClassVar, Generator, Generic, Iterator, List, Optional, Set, Tuple, Union

from vellum import (
    AdHocExecutePromptEvent,
    AdHocExpandMeta,
    ChatMessage,
    FunctionDefinition,
    PromptBlock,
    PromptOutput,
    PromptParameters,
    PromptRequestChatHistoryInput,
    PromptRequestInput,
    PromptRequestJsonInput,
    PromptRequestStringInput,
    VellumVariable,
)
from vellum.client import ApiError, RequestOptions
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.prompt_exec_config import PromptExecConfig
from vellum.client.types.prompt_settings import PromptSettings
from vellum.client.types.rich_text_child_block import RichTextChildBlock
from vellum.workflows.context import get_execution_context
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.errors.types import vellum_error_to_workflow_error
from vellum.workflows.events.types import default_serializer
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases.base_prompt_node import BasePromptNode
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType, is_workflow_class
from vellum.workflows.utils.functions import compile_function_definition, compile_workflow_function_definition


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
    expand_meta: Optional[AdHocExpandMeta] = None

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

        normalized_functions: Optional[List[FunctionDefinition]] = None

        if self.functions:
            normalized_functions = []
            for function in self.functions:
                if isinstance(function, FunctionDefinition):
                    normalized_functions.append(function)
                elif is_workflow_class(function):
                    normalized_functions.append(compile_workflow_function_definition(function))
                else:
                    normalized_functions.append(compile_function_definition(function))

        if self.settings and not self.settings.stream_enabled:
            # This endpoint is returning a single event, so we need to wrap it in a generator
            # to match the existing interface.
            response = self._context.vellum_client.ad_hoc.adhoc_execute_prompt(
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
            return iter([response])
        else:
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

    def _process_prompt_event_stream(self) -> Generator[BaseOutput, None, Optional[List[PromptOutput]]]:
        try:
            # Compile dict blocks into PromptBlocks
            exec_config = PromptExecConfig.model_validate(
                {
                    "ml_model": "",
                    "input_variables": [],
                    "parameters": {},
                    "blocks": self.blocks,
                }
            )
            self.blocks = exec_config.blocks  # type: ignore
        except Exception:
            raise NodeException(
                message="Failed to compile blocks",
                code=WorkflowErrorCode.INVALID_INPUTS,
            )

        self._validate()
        try:
            prompt_event_stream = self._get_prompt_event_stream()
        except ApiError as e:
            self._handle_api_error(e)

        if not self.settings or (self.settings and self.settings.stream_enabled):
            # We don't use the INITIATED event anyway, so we can just skip it
            # and use the exception handling to catch other api level errors
            try:
                next(prompt_event_stream)
            except ApiError as e:
                self._handle_api_error(e)

        outputs: Optional[List[PromptOutput]] = None
        for event in prompt_event_stream:
            if event.state == "INITIATED":
                continue
            elif event.state == "STREAMING":
                yield BaseOutput(name="results", delta=event.output.value)
            elif event.state == "FULFILLED":
                outputs = event.outputs
                yield BaseOutput(name="results", value=event.outputs)
            elif event.state == "REJECTED":
                workflow_error = vellum_error_to_workflow_error(event.error)
                raise NodeException.of(workflow_error)

        return outputs

    def _compile_prompt_inputs(self) -> Tuple[List[VellumVariable], List[PromptRequestInput]]:
        input_variables: List[VellumVariable] = []
        input_values: List[PromptRequestInput] = []

        if not self.prompt_inputs:
            return input_variables, input_values

        for input_name, input_value in self.prompt_inputs.items():
            # Exclude inputs that resolved to be null. This ensure that we don't pass input values
            # to optional prompt inputs whose values were unresolved.
            if input_value is None:
                continue
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
