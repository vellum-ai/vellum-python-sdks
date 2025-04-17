import pytest
from uuid import uuid4
from typing import Type

from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.generics import NodeType
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import (
    NodeDisplays,
    NodeOutputDisplays,
    StateValueDisplays,
    WorkflowDisplayContext,
    WorkflowInputsDisplays,
)
from vellum_ee.workflows.display.vellum import WorkflowMetaVellumDisplay
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


@pytest.fixture()
def serialize_node():
    def _serialize_node(
        node_class: Type[NodeType],
        global_workflow_input_displays: WorkflowInputsDisplays = {},
        global_state_value_displays: StateValueDisplays = {},
        global_node_displays: NodeDisplays = {},
        global_node_output_displays: NodeOutputDisplays = {},
    ) -> JsonObject:
        node_display_class = get_node_display_class(node_class)
        node_display = node_display_class()

        context: WorkflowDisplayContext = WorkflowDisplayContext(
            workflow_display_class=BaseWorkflowDisplay,
            workflow_display=WorkflowMetaVellumDisplay(
                entrypoint_node_id=uuid4(),
                entrypoint_node_source_handle_id=uuid4(),
                entrypoint_node_display=NodeDisplayData(),
            ),
            node_displays={node_class: node_display},
            global_workflow_input_displays=global_workflow_input_displays,
            global_state_value_displays=global_state_value_displays,
            global_node_displays=global_node_displays,
            global_node_output_displays=global_node_output_displays,
        )
        return node_display.serialize(context)

    return _serialize_node
