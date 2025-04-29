from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap

from .....nodes.parse_function_call.nodes.conditional_node_1 import ConditionalNode2


class ConditionalNode2Display(BaseConditionalNodeDisplay[ConditionalNode2]):
    label = "Conditional Node"
    node_id = UUID("f5ccd090-d6f8-44c8-8e1a-23abb3e0cce2")
    target_handle_id = UUID("ec011887-0213-4667-90d3-fcf0b1e170ca")
    source_handle_ids = {
        0: UUID("f40a1638-e846-4aa1-9dda-0d5fe439697a"),
        1: UUID("a58748f1-8ae4-470f-9e3e-80478f567f5d"),
    }
    rule_ids = [
        RuleIdMap(
            id="d16245e8-5465-4f2c-a7e9-f7091e6ad2dd",
            lhs=RuleIdMap(
                id="1a4cc082-17bf-4cd3-bd9d-f84b209a5008",
                lhs=None,
                rhs=None,
                field_node_input_id="839e9337-765e-4a3a-a8ca-74acb91014a2",
                value_node_input_id="754fa31d-451d-4669-977b-8d5f23a4b542",
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        )
    ]
    condition_ids = [
        ConditionId(id="4ca649ff-199b-4f31-8bf5-57063305d35c", rule_group_id="d16245e8-5465-4f2c-a7e9-f7091e6ad2dd"),
        ConditionId(id="1c58d548-5ea6-4037-b4e6-589a98a911af", rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "5b5a07bf-0b78-48bb-8fdc-ae0c0c5266b7.field": UUID("839e9337-765e-4a3a-a8ca-74acb91014a2"),
        "5b5a07bf-0b78-48bb-8fdc-ae0c0c5266b7.value": UUID("754fa31d-451d-4669-977b-8d5f23a4b542"),
    }
    port_displays = {
        ConditionalNode2.Ports.branch_1: PortDisplayOverrides(id=UUID("f40a1638-e846-4aa1-9dda-0d5fe439697a")),
        ConditionalNode2.Ports.branch_2: PortDisplayOverrides(id=UUID("a58748f1-8ae4-470f-9e3e-80478f567f5d")),
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=4515, y=885), width=None, height=None)
