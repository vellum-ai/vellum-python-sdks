import inspect
from uuid import UUID
from typing import ClassVar, Generic, Optional, TypeVar

from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.nodes.displayable.code_execution_node.utils import read_file_from_path
from vellum.workflows.types.core import JsonObject
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_CodeExecutionNodeType = TypeVar("_CodeExecutionNodeType", bound=CodeExecutionNode)


class BaseCodeExecutionNodeDisplay(BaseNodeVellumDisplay[_CodeExecutionNodeType], Generic[_CodeExecutionNodeType]):
    output_id: ClassVar[Optional[UUID]] = None
    log_output_id: ClassVar[Optional[UUID]] = None

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id
        raw_code = raise_if_descriptor(node.code)
        filepath = raise_if_descriptor(node.filepath)

        code_value: Optional[str]
        if raw_code:
            code_value = raw_code
        elif filepath:
            node_file_path = inspect.getfile(node)
            file_code = read_file_from_path(
                node_filepath=node_file_path,
                script_filepath=filepath,
            )
            code_value = file_code
        else:
            code_value = ""

        code_inputs = raise_if_descriptor(node.code_inputs)

        inputs = [
            create_node_input(
                node_id=node_id,
                input_name=variable_name,
                value=variable_value,
                display_context=display_context,
                input_id=self.node_input_ids_by_name.get(f"{CodeExecutionNode.code_inputs.name}.{variable_name}")
                or self.node_input_ids_by_name.get(variable_name),
            )
            for variable_name, variable_value in code_inputs.items()
        ]

        code_input_id = self.node_input_ids_by_name.get(CodeExecutionNode.code.name)
        code_node_input = create_node_input(
            node_id=node_id,
            input_name="code",
            value=code_value,
            display_context=display_context,
            input_id=code_input_id,
        )

        runtime_input_id = self.node_input_ids_by_name.get(CodeExecutionNode.runtime.name)
        runtime_node_input = create_node_input(
            node_id=node_id,
            input_name="runtime",
            value=node.runtime,
            display_context=display_context,
            input_id=runtime_input_id,
        )
        inputs.extend([code_node_input, runtime_node_input])

        packages = raise_if_descriptor(node.packages)

        _, output_display = display_context.global_node_output_displays[node.Outputs.result]
        _, log_output_display = display_context.global_node_output_displays[node.Outputs.log]

        output_type = primitive_type_to_vellum_variable_type(node.get_output_type())

        return {
            "id": str(node_id),
            "type": "CODE_EXECUTION",
            "inputs": [input.dict() for input in inputs],
            "data": {
                "label": self.label,
                "error_output_id": str(error_output_id) if error_output_id else None,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "code_input_id": code_node_input.id,
                "runtime_input_id": runtime_node_input.id,
                "output_type": output_type,
                "packages": [package.dict() for package in packages] if packages is not None else [],
                "output_id": str(self.output_id) if self.output_id else str(output_display.id),
                "log_output_id": str(self.log_output_id) if self.log_output_id else str(log_output_display.id),
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }
