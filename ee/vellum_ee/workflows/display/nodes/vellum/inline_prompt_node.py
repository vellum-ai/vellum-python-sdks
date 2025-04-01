from uuid import UUID
from typing import Callable, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from vellum import FunctionDefinition, PromptBlock, RichTextChildBlock, VellumVariable
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.utils.functions import compile_function_definition
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type
from vellum_ee.workflows.display.vellum import NodeInput

_InlinePromptNodeType = TypeVar("_InlinePromptNodeType", bound=InlinePromptNode)


class BaseInlinePromptNodeDisplay(BaseNodeVellumDisplay[_InlinePromptNodeType], Generic[_InlinePromptNodeType]):
    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        node_inputs, prompt_inputs = self._generate_node_and_prompt_inputs(node_id, node, display_context)
        input_variable_id_by_name = {prompt_input.key: prompt_input.id for prompt_input in prompt_inputs}

        _, output_display = display_context.global_node_output_displays[node.Outputs.text]
        _, array_display = display_context.global_node_output_displays[node.Outputs.results]
        _, json_display = display_context.global_node_output_displays[node.Outputs.json]
        node_blocks = raise_if_descriptor(node.blocks)
        function_definitions = raise_if_descriptor(node.functions)

        blocks: list = [
            self._generate_prompt_block(block, input_variable_id_by_name, [i]) for i, block in enumerate(node_blocks)
        ]
        functions = (
            [self._generate_function_tools(function, i) for i, function in enumerate(function_definitions)]
            if function_definitions
            else []
        )
        blocks.extend(functions)

        return {
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
                    "parameters": raise_if_descriptor(node.parameters).dict(),
                    "input_variables": [prompt_input.dict() for prompt_input in prompt_inputs],
                    "prompt_template_block_data": {
                        "version": 1,
                        "blocks": blocks,
                    },
                },
                "ml_model_name": raise_if_descriptor(node.ml_model),
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
            "outputs": [
                {"id": str(json_display.id), "name": "json", "type": "JSON", "value": None},
                {"id": str(output_display.id), "name": "text", "type": "STRING", "value": None},
                {"id": str(array_display.id), "name": "results", "type": "ARRAY", "value": None},
            ],
        }

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

    def _generate_function_tools(self, function: Union[FunctionDefinition, Callable], index: int) -> JsonObject:
        normalized_functions = (
            function if isinstance(function, FunctionDefinition) else compile_function_definition(function)
        )
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
            block = {
                "block_type": "VARIABLE",
                "input_variable_id": input_variable_id_by_name[prompt_block.input_variable],
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

        block["id"] = str(
            uuid4_from_hash(f"{self.node_id}-{prompt_block.block_type}-{'-'.join([str(i) for i in path])}")
        )
        if prompt_block.cache_config:
            block["cache_config"] = prompt_block.cache_config.dict()
        else:
            block["cache_config"] = None

        if prompt_block.state:
            block["state"] = prompt_block.state
        else:
            block["state"] = "ENABLED"

        return block
