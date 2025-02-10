import pytest
from uuid import uuid4
from typing import Any, Dict, Tuple, Type

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.output import OutputReference
from vellum.workflows.references.state_value import StateValueReference
from vellum.workflows.references.workflow_input import WorkflowInputReference
from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.generics import NodeType
from vellum_ee.workflows.display.base import StateValueDisplayType, WorkflowInputsDisplayType
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.types import NodeDisplayType, WorkflowDisplayContext
from vellum_ee.workflows.display.vellum import NodeDisplayData, WorkflowMetaVellumDisplay
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


@pytest.fixture()
def serialize_node():
    def _serialize_node(
        node_class: Type[NodeType],
        base_class: type[BaseNodeDisplay[Any]] = BaseNodeDisplay,
        global_workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = {},
        global_state_value_displays: Dict[StateValueReference, StateValueDisplayType] = {},
        global_node_displays: Dict[Type[BaseNode], NodeDisplayType] = {},
        global_node_output_displays: Dict[OutputReference, Tuple[Type[BaseNode], NodeOutputDisplay]] = {},
    ) -> JsonObject:
        node_display_class = get_node_display_class(base_class, node_class)
        node_display = node_display_class()

        context: WorkflowDisplayContext = WorkflowDisplayContext(
            workflow_display_class=VellumWorkflowDisplay,
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
