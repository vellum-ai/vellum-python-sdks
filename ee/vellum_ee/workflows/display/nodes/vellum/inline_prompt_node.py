from uuid import UUID
from typing import TYPE_CHECKING, Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from vellum import FunctionDefinition, PromptBlock, RichTextChildBlock, VellumVariable
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.definition import DeploymentDefinition, VellumIntegrationToolDefinition
from vellum.workflows.types.generics import is_workflow_class
from vellum.workflows.utils.functions import (
    compile_function_definition,
    compile_inline_workflow_function_definition,
    compile_vellum_integration_tool_definition,
    compile_workflow_deployment_function_definition,
)
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type
from vellum_ee.workflows.display.vellum import NodeInput

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow


def _contains_descriptors(obj):
    """Check if an object contains any descriptors or references that need special handling."""
    if isinstance(obj, BaseDescriptor):
        return True
    elif isinstance(obj, dict):
        return any(_contains_descriptors(v) for v in obj.values())
    elif isinstance(obj, (list, tuple)):
        return any(_contains_descriptors(item) for item in obj)
    elif hasattr(obj, "__dict__"):
        return any(_contains_descriptors(getattr(obj, field)) for field in obj.__dict__)
    return False


_InlinePromptNodeType = TypeVar("_InlinePromptNodeType", bound=InlinePromptNode)


class BaseInlinePromptNodeDisplay(BaseNodeDisplay[_InlinePromptNodeType], Generic[_InlinePromptNodeType]):
    __serializable_inputs__ = {
        InlinePromptNode.prompt_inputs,
    }
    __unserializable_attributes__ = {
        InlinePromptNode.settings,
        InlinePromptNode.expand_meta,
        InlinePromptNode.request_options,
    }

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **_kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        node_inputs, prompt_inputs = self._generate_node_and_prompt_inputs(node_id, node, display_context)
        input_variable_id_by_name = {prompt_input.key: prompt_input.id for prompt_input in prompt_inputs}

        output_display = self.output_display[node.Outputs.text]
        array_display = self.output_display[node.Outputs.results]
        json_display = self.output_display[node.Outputs.json]
        node_blocks = raise_if_descriptor(node.blocks) or []
        function_definitions = raise_if_descriptor(node.functions)

        ml_model = str(raise_if_descriptor(node.ml_model))

        has_descriptors = _contains_descriptors(node_blocks)

        blocks: list = []
        if not has_descriptors:
            blocks = [
                self._generate_prompt_block(block, input_variable_id_by_name, [i])
                for i, block in enumerate(node_blocks)
                if not isinstance(block, BaseDescriptor)
            ]

        functions = (
            [
                self._generate_function_tools(function, i, display_context)
                for i, function in enumerate(function_definitions)
            ]
            if isinstance(function_definitions, list)
            else []
        )
        blocks.extend(functions)

        serialized_node: JsonObject = {
            "id": str(node_id),
            "type": "PROMPT",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "output_id": str(output_display.id),
                "error_output_id": str(error_output_id) if error_output_id else None,
                "array_output_id": str(array_display.id),
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "variant": "INLINE",
                "exec_config": {
                    "parameters": self._serialize_parameters(node.parameters, display_context),
                    "input_variables": [prompt_input.dict() for prompt_input in prompt_inputs],
                    "prompt_template_block_data": {
                        "version": 1,
                        "blocks": blocks,
                    },
                },
                "ml_model_name": ml_model,
            },
            **self.serialize_generic_fields(display_context, exclude=["outputs"]),
            "outputs": [
                {"id": str(json_display.id), "name": "json", "type": "JSON", "value": None},
                {"id": str(output_display.id), "name": "text", "type": "STRING", "value": None},
                {"id": str(array_display.id), "name": "results", "type": "ARRAY", "value": None},
            ],
        }
        attributes = self._serialize_attributes(display_context)
        if attributes:
            serialized_node["attributes"] = attributes
        return serialized_node

    def _generate_node_and_prompt_inputs(
        self,
        node_id: UUID,
        node: Type[InlinePromptNode],
        display_context: WorkflowDisplayContext,
    ) -> Tuple[List[NodeInput], List[VellumVariable]]:
        value = raise_if_descriptor(node.prompt_inputs)

        node_inputs: List[NodeInput] = []
        prompt_inputs: List[VellumVariable] = []

        if not value:
            return node_inputs, prompt_inputs

        for variable_name, variable_value in value.items():
            node_input = create_node_input(
                node_id=node_id,
                input_name=variable_name,
                value=variable_value,
                display_context=display_context,
                input_id=self.node_input_ids_by_name.get(f"{InlinePromptNode.prompt_inputs.name}.{variable_name}")
                or self.node_input_ids_by_name.get(variable_name),
            )
            vellum_variable_type = infer_vellum_variable_type(variable_value)
            node_inputs.append(node_input)
            prompt_inputs.append(VellumVariable(id=str(node_input.id), key=variable_name, type=vellum_variable_type))

        return node_inputs, prompt_inputs

    def _generate_function_tools(
        self,
        function: Union[FunctionDefinition, Callable, DeploymentDefinition, Type["BaseWorkflow"]],
        index: int,
        display_context: WorkflowDisplayContext,
    ) -> JsonObject:
        if isinstance(function, FunctionDefinition):
            normalized_functions = function
        elif is_workflow_class(function):
            normalized_functions = compile_inline_workflow_function_definition(function)
        elif callable(function):
            normalized_functions = compile_function_definition(function)
        elif isinstance(function, DeploymentDefinition):
            normalized_functions = compile_workflow_deployment_function_definition(function, display_context.client)
        elif isinstance(function, VellumIntegrationToolDefinition):
            normalized_functions = compile_vellum_integration_tool_definition(function, display_context.client)
        else:
            raise ValueError(f"Unsupported function type: {type(function)}")
        return {
            "id": str(uuid4_from_hash(f"{self.node_id}-FUNCTION_DEFINITION-{index}")),
            "block_type": "FUNCTION_DEFINITION",
            "properties": {
                "function_name": normalized_functions.name,
                "function_description": normalized_functions.description,
                "function_parameters": normalized_functions.parameters,
                "function_forced": normalized_functions.forced,
                "function_strict": normalized_functions.strict,
            },
        }

    def _generate_prompt_block(
        self,
        prompt_block: Union[PromptBlock, RichTextChildBlock],
        input_variable_id_by_name: Dict[str, str],
        path: List[int],
    ) -> JsonObject:
        block: JsonObject
        block_id = uuid4_from_hash(f"{self.node_id}-{prompt_block.block_type}-{'-'.join([str(i) for i in path])}")
        if prompt_block.block_type == "JINJA":
            block = {
                "block_type": "JINJA",
                "properties": {"template": prompt_block.template, "template_type": "STRING"},
            }

        elif prompt_block.block_type == "CHAT_MESSAGE":
            chat_properties: JsonObject = {
                "chat_role": prompt_block.chat_role,
                "chat_source": prompt_block.chat_source,
                "chat_message_unterminated": bool(prompt_block.chat_message_unterminated),
                "blocks": [
                    self._generate_prompt_block(block, input_variable_id_by_name, path + [i])
                    for i, block in enumerate(prompt_block.blocks)
                ],
            }

            block = {
                "block_type": "CHAT_MESSAGE",
                "properties": chat_properties,
            }

        elif prompt_block.block_type == "FUNCTION_DEFINITION":
            block = {
                "block_type": "FUNCTION_DEFINITION",
                "properties": {
                    "function_name": prompt_block.function_name,
                    "function_description": prompt_block.function_description,
                    "function_parameters": prompt_block.function_parameters,
                    "function_forced": prompt_block.function_forced,
                    "function_strict": prompt_block.function_strict,
                },
            }

        elif prompt_block.block_type == "VARIABLE":
            input_variable_id = input_variable_id_by_name.get(prompt_block.input_variable)
            if input_variable_id:
                block = {
                    "block_type": "VARIABLE",
                    "input_variable_id": input_variable_id,
                }
            else:
                # Even though this will likely fail in runtime, we want to allow serialization to succeed
                # in case the block is work in progress or the node is not yet part of the graph
                block = {
                    "block_type": "VARIABLE",
                    "input_variable_id": str(
                        uuid4_from_hash(f"{block_id}-input_variable-{prompt_block.input_variable}")
                    ),
                }

        elif prompt_block.block_type == "PLAIN_TEXT":
            block = {
                "block_type": "PLAIN_TEXT",
                "text": prompt_block.text,
            }

        elif prompt_block.block_type == "RICH_TEXT":
            block = {
                "block_type": "RICH_TEXT",
                "blocks": [
                    self._generate_prompt_block(child, input_variable_id_by_name, path + [i])
                    for i, child in enumerate(prompt_block.blocks)
                ],
            }
        else:
            raise NotImplementedError(f"Serialization for prompt block type {prompt_block.block_type} not implemented")

        block["id"] = str(block_id)
        if prompt_block.cache_config:
            block["cache_config"] = prompt_block.cache_config.dict()
        else:
            block["cache_config"] = None

        if prompt_block.state:
            block["state"] = prompt_block.state
        else:
            block["state"] = "ENABLED"

        return block

    def _serialize_parameters(self, parameters, display_context: "WorkflowDisplayContext") -> JsonObject:
        """Serialize parameters, returning empty object when nested descriptors are detected."""
        params = raise_if_descriptor(parameters)
        if not params:
            return {}

        if _contains_descriptors(params):
            return {}

        return params.dict()
