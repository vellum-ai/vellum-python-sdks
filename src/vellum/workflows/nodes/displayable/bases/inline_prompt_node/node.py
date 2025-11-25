from itertools import chain
import json
from uuid import uuid4
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Generator,
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

import httpx

from vellum import (
    AdHocExecutePromptEvent,
    AdHocExpandMeta,
    ChatMessage,
    FunctionDefinition,
    InitiatedAdHocExecutePromptEvent,
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
from vellum.client.types import (
    PromptRequestAudioInput,
    PromptRequestDocumentInput,
    PromptRequestImageInput,
    PromptRequestVideoInput,
    VellumAudio,
    VellumAudioRequest,
    VellumDocument,
    VellumDocumentRequest,
    VellumImage,
    VellumImageRequest,
    VellumVideo,
    VellumVideoRequest,
)
from vellum.client.types.chat_message_request import ChatMessageRequest
from vellum.client.types.prompt_exec_config import PromptExecConfig
from vellum.client.types.prompt_settings import PromptSettings
from vellum.client.types.rich_text_child_block import RichTextChildBlock
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows.context import get_execution_context
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.errors.types import vellum_error_to_workflow_error
from vellum.workflows.events.types import default_serializer
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.bases.base_prompt_node import BasePromptNode
from vellum.workflows.nodes.displayable.bases.utils import process_additional_prompt_outputs
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.definition import (
    ComposioToolDefinition,
    DeploymentDefinition,
    MCPServer,
    VellumIntegrationToolDefinition,
)
from vellum.workflows.types.generics import StateType, is_workflow_class
from vellum.workflows.utils.functions import (
    compile_composio_tool_definition,
    compile_function_definition,
    compile_inline_workflow_function_definition,
    compile_mcp_tool_definition,
    compile_vellum_integration_tool_definition,
    compile_workflow_deployment_function_definition,
    get_mcp_tool_name,
)
from vellum.workflows.utils.pydantic_schema import normalize_json

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow


def _is_json_schema_type(schema: dict, schema_type: str) -> bool:
    """
    Check if a JSON schema has a specific type.
    Handles both single type strings and arrays of types.
    """
    type_value = schema.get("type")
    if isinstance(type_value, list):
        return schema_type in type_value
    return type_value == schema_type


def _get_json_schema_to_validate(parameters_ref: object) -> tuple:
    """
    Extracts the JSON schema to validate from a parameters reference.

    Also normalizes Pydantic models to JSON schema dicts so they can be validated.

    Args:
        parameters_ref: The parameters reference (NodeReference wrapping PromptParameters)

    Returns:
        A tuple of (schema_dict, path_string) where schema_dict is the schema to validate
        and path_string is the path for error messages. Returns (None, "") if no schema found.
    """
    parameters_instance = getattr(parameters_ref, "instance", None)
    if not parameters_instance:
        return None, ""

    custom_params = getattr(parameters_instance, "custom_parameters", None)
    if not isinstance(custom_params, dict):
        return None, ""

    json_schema = custom_params.get("json_schema")
    if json_schema is None:
        return None, ""

    # Normalize Pydantic models to JSON schema dicts before validation
    # This handles cases like {"name": "...", "schema": SomePydanticModel}
    json_schema = normalize_json(json_schema)

    # After normalization, we expect a dict; anything else we ignore
    if not isinstance(json_schema, dict):
        return None, ""

    return json_schema, "parameters.custom_parameters.json_schema"


def _validate_json_schema_structure(schema: dict, path: str = "json_schema") -> None:
    """
    Validates the structure of a JSON schema to catch common errors early.

    This validation focuses on structural requirements that would cause errors
    during workflow execution. It checks:
    - Array types have an 'items' field (unless using 'prefixItems')
    - Object types have valid 'properties' structure
    - Composition keywords (anyOf, oneOf, allOf) contain valid sub-schemas

    Args:
        schema: The JSON schema dictionary to validate
        path: The current path in the schema (for error messages)

    Raises:
        ValueError: If the schema structure is invalid
    """
    if not isinstance(schema, dict):
        return

    # Validate array types
    if _is_json_schema_type(schema, "array"):
        has_prefix_items = "prefixItems" in schema
        has_items = "items" in schema

        # Array schemas must have either 'items' or 'prefixItems' defined
        if not has_prefix_items and not has_items:
            raise ValueError(
                f"JSON Schema of type 'array' at '{path}' must define either an 'items' field "
                f"or a 'prefixItems' field to specify the type of elements in the array."
            )

        # Recursively validate the items schema
        if has_items:
            items_schema = schema["items"]
            # Single-schema items: recurse once
            if isinstance(items_schema, dict):
                _validate_json_schema_structure(items_schema, f"{path}.items")
            # Tuple-style items: list of schemas
            elif isinstance(items_schema, list):
                for idx, sub_schema in enumerate(items_schema):
                    if isinstance(sub_schema, dict):
                        _validate_json_schema_structure(sub_schema, f"{path}.items[{idx}]")
                    else:
                        raise ValueError(
                            f"JSON Schema 'items[{idx}]' at '{path}.items[{idx}]' must be a schema object, "
                            f"not {type(sub_schema).__name__}"
                        )
            else:
                # items must be a schema object or a list of schema objects
                raise ValueError(
                    f"JSON Schema 'items' field at '{path}.items' must be a schema object or a list of schema "
                    f"objects, not {type(items_schema).__name__}"
                )

        # Recursively validate prefixItems schemas
        if has_prefix_items:
            prefix_items = schema["prefixItems"]
            if not isinstance(prefix_items, list):
                raise ValueError(
                    f"JSON Schema 'prefixItems' field at '{path}.prefixItems' must be a list of schema objects, "
                    f"not {type(prefix_items).__name__}"
                )
            for idx, sub_schema in enumerate(prefix_items):
                if isinstance(sub_schema, dict):
                    _validate_json_schema_structure(sub_schema, f"{path}.prefixItems[{idx}]")
                else:
                    raise ValueError(
                        f"JSON Schema 'prefixItems[{idx}]' at '{path}.prefixItems[{idx}]' must be a schema object, "
                        f"not {type(sub_schema).__name__}"
                    )

    # Validate object types
    if _is_json_schema_type(schema, "object"):
        properties = schema.get("properties")
        if properties is not None and not isinstance(properties, dict):
            raise ValueError(
                f"JSON Schema of type 'object' at '{path}' must have 'properties' defined as a dictionary, "
                f"not {type(properties).__name__}"
            )

        # Recursively validate nested properties
        if isinstance(properties, dict):
            for key, value in properties.items():
                if isinstance(value, dict):
                    _validate_json_schema_structure(value, f"{path}.properties.{key}")
                else:
                    raise ValueError(
                        f"JSON Schema property '{key}' at '{path}.properties.{key}' must be a schema object, "
                        f"not {type(value).__name__}"
                    )

    # Validate composition keywords
    for keyword in ["anyOf", "oneOf", "allOf"]:
        if keyword in schema:
            value = schema[keyword]
            if not isinstance(value, list):
                raise ValueError(
                    f"JSON Schema's '{keyword}' field at '{path}' must be a list of schemas, "
                    f"not {type(value).__name__}"
                )
            # Recursively validate each sub-schema
            for i, sub_schema in enumerate(value):
                if isinstance(sub_schema, dict):
                    _validate_json_schema_structure(sub_schema, f"{path}.{keyword}[{i}]")
                else:
                    raise ValueError(
                        f"JSON Schema '{keyword}[{i}]' at '{path}.{keyword}[{i}]' must be a schema object, "
                        f"not {type(sub_schema).__name__}"
                    )

    # Handle structured-output wrappers: {"name": "...", "schema": {...}}
    # Recursively validate the nested schema field if present
    if "schema" in schema:
        inner_schema = schema["schema"]
        if isinstance(inner_schema, dict):
            _validate_json_schema_structure(inner_schema, f"{path}.schema")
        else:
            raise ValueError(
                f"JSON Schema 'schema' field at '{path}.schema' must be a schema object, "
                f"not {type(inner_schema).__name__}"
            )


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
    functions: Optional[
        List[
            Union[
                FunctionDefinition,
                Callable,
                DeploymentDefinition,
                Type["BaseWorkflow"],
                VellumIntegrationToolDefinition,
                MCPServer,
            ]
        ]
    ] = None

    parameters: PromptParameters = DEFAULT_PROMPT_PARAMETERS
    expand_meta: Optional[AdHocExpandMeta] = AdHocExpandMeta(finish_reason=True)

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

        processed_parameters = self.process_parameters(self.parameters)
        processed_blocks = self.process_blocks(self.blocks)

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
                elif isinstance(function, DeploymentDefinition):
                    normalized_functions.append(
                        compile_workflow_deployment_function_definition(
                            function,
                            vellum_client=self._context.vellum_client,
                        )
                    )
                elif is_workflow_class(function):
                    normalized_functions.append(compile_inline_workflow_function_definition(function))
                elif callable(function):
                    normalized_functions.append(compile_function_definition(function))
                elif isinstance(function, ComposioToolDefinition):
                    normalized_functions.append(compile_composio_tool_definition(function))
                elif isinstance(function, VellumIntegrationToolDefinition):
                    normalized_functions.append(
                        compile_vellum_integration_tool_definition(function, self._context.vellum_client)
                    )
                elif isinstance(function, MCPServer):
                    tool_definitions = compile_mcp_tool_definition(function)
                    for tool_def in tool_definitions:
                        normalized_functions.append(
                            FunctionDefinition(
                                name=get_mcp_tool_name(tool_def),
                                description=tool_def.description,
                                parameters=tool_def.parameters,
                            )
                        )
                else:
                    raise NodeException(
                        message=f"`{function}` is not a valid function definition",
                        code=WorkflowErrorCode.INVALID_INPUTS,
                    )

        if self.settings and not self.settings.stream_enabled:
            # This endpoint is returning a single event, so we need to wrap it in a generator
            # to match the existing interface.
            response = self._context.vellum_client.ad_hoc.adhoc_execute_prompt(
                ml_model=self.ml_model,
                input_values=input_values,
                input_variables=input_variables,
                parameters=processed_parameters,
                blocks=processed_blocks,
                settings=self.settings,
                functions=normalized_functions,
                expand_meta=self.expand_meta,
                request_options=request_options,
            )
            initiated_event = InitiatedAdHocExecutePromptEvent(execution_id=response.execution_id)
            return iter([initiated_event, response])
        else:
            return self._context.vellum_client.ad_hoc.adhoc_execute_prompt_stream(
                ml_model=self.ml_model,
                input_values=input_values,
                input_variables=input_variables,
                parameters=processed_parameters,
                blocks=processed_blocks,
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
        except httpx.TransportError:
            raise NodeException(
                message="Failed to connect to Vellum server",
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )

        try:
            first_event = next(prompt_event_stream)
        except ApiError as e:
            self._handle_api_error(e)
        except httpx.TransportError:
            raise NodeException(
                message="Failed to connect to Vellum server",
                code=WorkflowErrorCode.INTERNAL_ERROR,
            )
        else:
            if first_event.state == "REJECTED":
                workflow_error = vellum_error_to_workflow_error(first_event.error)
                raise NodeException.of(workflow_error)
            if first_event.state != "INITIATED":
                prompt_event_stream = chain([first_event], prompt_event_stream)

        outputs: Optional[List[PromptOutput]] = None
        for event in prompt_event_stream:
            if event.state == "INITIATED":
                continue
            elif event.state == "STREAMING":
                yield BaseOutput(name="results", delta=event.output.value)
            elif event.state == "FULFILLED":
                if event.meta and event.meta.finish_reason == "LENGTH":
                    text_value, json_value = process_additional_prompt_outputs(event.outputs)
                    if text_value == "":
                        raise NodeException(
                            message=(
                                "Maximum tokens reached before model could output any content. "
                                "Consider increasing the max_tokens Prompt Parameter."
                            ),
                            code=WorkflowErrorCode.INVALID_OUTPUTS,
                        )

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
            elif isinstance(input_value, (VellumAudio, VellumAudioRequest)):
                input_variables.append(
                    VellumVariable(
                        id=str(uuid4()),
                        key=input_name,
                        type="AUDIO",
                    )
                )
                input_values.append(
                    PromptRequestAudioInput(
                        key=input_name,
                        value=(
                            input_value
                            if isinstance(input_value, VellumAudio)
                            else VellumAudio.model_validate(input_value.model_dump())
                        ),
                    )
                )
            elif isinstance(input_value, (VellumVideo, VellumVideoRequest)):
                input_variables.append(
                    VellumVariable(
                        id=str(uuid4()),
                        key=input_name,
                        type="VIDEO",
                    )
                )
                input_values.append(
                    PromptRequestVideoInput(
                        key=input_name,
                        value=(
                            input_value
                            if isinstance(input_value, VellumVideo)
                            else VellumVideo.model_validate(input_value.model_dump())
                        ),
                    )
                )
            elif isinstance(input_value, (VellumImage, VellumImageRequest)):
                input_variables.append(
                    VellumVariable(
                        id=str(uuid4()),
                        key=input_name,
                        type="IMAGE",
                    )
                )
                input_values.append(
                    PromptRequestImageInput(
                        key=input_name,
                        value=(
                            input_value
                            if isinstance(input_value, VellumImage)
                            else VellumImage.model_validate(input_value.model_dump())
                        ),
                    )
                )
            elif isinstance(input_value, (VellumDocument, VellumDocumentRequest)):
                input_variables.append(
                    VellumVariable(
                        id=str(uuid4()),
                        key=input_name,
                        type="DOCUMENT",
                    )
                )
                input_values.append(
                    PromptRequestDocumentInput(
                        key=input_name,
                        value=(
                            input_value
                            if isinstance(input_value, VellumDocument)
                            else VellumDocument.model_validate(input_value.model_dump())
                        ),
                    )
                )
            elif (
                isinstance(input_value, dict)
                and "src" in input_value
                and isinstance(input_value.get("src"), str)
                and input_value["src"].endswith(".pdf")
            ):
                input_variables.append(
                    VellumVariable(
                        id=str(uuid4()),
                        key=input_name,
                        type="DOCUMENT",
                    )
                )
                input_values.append(
                    PromptRequestDocumentInput(
                        key=input_name,
                        value=VellumDocument.model_validate(input_value),
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

    def process_parameters(self, parameters: PromptParameters) -> PromptParameters:
        """
        Process parameters to recursively convert any Pydantic models to JSON schema dictionaries.
        """
        if not parameters.custom_parameters:
            return parameters

        processed_custom_params = normalize_json(parameters.custom_parameters)

        return parameters.model_copy(update={"custom_parameters": processed_custom_params})

    def process_blocks(self, blocks: List[PromptBlock]) -> List[PromptBlock]:
        """
        Override this method to process the blocks before they are executed.
        """
        return blocks

    @classmethod
    def __validate__(cls) -> None:
        """
        Validates the node configuration, including JSON schema structure in parameters.

        Raises:
            ValueError: If the node configuration is invalid
        """
        super().__validate__()

        parameters_ref = getattr(cls, "parameters", None)
        if parameters_ref is None:
            return

        schema, path = _get_json_schema_to_validate(parameters_ref)
        if schema is not None:
            _validate_json_schema_structure(schema, path=path)
