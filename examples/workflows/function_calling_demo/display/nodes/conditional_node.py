from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap

from ...nodes.conditional_node import ConditionalNode


class ConditionalNodeDisplay(BaseConditionalNodeDisplay[ConditionalNode]):
    label = "Conditional Node"
    node_id = UUID("a3f2fd3d-0c58-48d8-bdfc-9f16591b1964")
    target_handle_id = UUID("e07139df-febe-43fb-8e2c-11b85464dcde")
    source_handle_ids = {
        0: UUID("b032aa36-545e-4499-b7ba-2750e19b61d1"),
        1: UUID("60b2218f-1481-41e3-bc39-943033285d76"),
    }
    rule_ids = [
        RuleIdMap(
            id="4913d8e4-6cfe-4826-b722-3af118d788c9",
            lhs=RuleIdMap(
                id="f860841f-da06-45c2-ad50-c63f975469a8",
                lhs=None,
                rhs=None,
                field_node_input_id="4dd04a7d-7a12-43b1-9a0b-b2dc182227c6",
                value_node_input_id="95b497b8-7357-4f74-a86f-b65f4ae14dcf",
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        )
    ]
    condition_ids = [
        ConditionId(id="708ee94b-62f1-46cf-ac1b-157548dd6e40", rule_group_id="4913d8e4-6cfe-4826-b722-3af118d788c9"),
        ConditionId(id="dbd8983a-63a5-432b-a1c7-4ddf612010f5", rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "226cdc38-6029-4e73-8d88-a283cd6dc0de.field": UUID("4dd04a7d-7a12-43b1-9a0b-b2dc182227c6"),
        "226cdc38-6029-4e73-8d88-a283cd6dc0de.value": UUID("95b497b8-7357-4f74-a86f-b65f4ae14dcf"),
    }
    port_displays = {
        ConditionalNode.Ports.branch_1: PortDisplayOverrides(id=UUID("b032aa36-545e-4499-b7ba-2750e19b61d1")),
        ConditionalNode.Ports.branch_2: PortDisplayOverrides(id=UUID("60b2218f-1481-41e3-bc39-943033285d76")),
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3405, y=-90), width=457, height=177)
