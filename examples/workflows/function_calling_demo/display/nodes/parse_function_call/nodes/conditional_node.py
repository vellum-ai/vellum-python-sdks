from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap

from .....nodes.parse_function_call.nodes.conditional_node import ConditionalNode1


class ConditionalNode1Display(BaseConditionalNodeDisplay[ConditionalNode1]):
    label = "Conditional Node"
    node_id = UUID("fb53aa28-21ac-41ff-8df5-0c6d25643b2c")
    target_handle_id = UUID("9f7922c6-23ca-4116-aa18-759406198e68")
    source_handle_ids = {
        0: UUID("1eca0f4d-7182-4b2e-873b-4030019a8bbd"),
        1: UUID("0c290732-913b-4490-a3bd-e43c23bbace4"),
    }
    rule_ids = [
        RuleIdMap(
            id="db16af99-4a75-4780-8bb0-56fb0a2931a3",
            lhs=RuleIdMap(
                id="75519ec6-2fc1-4dc0-ae32-392a70c30109",
                lhs=None,
                rhs=None,
                field_node_input_id="0362e67a-b95c-4d2e-94cb-0d748605e184",
                value_node_input_id=None,
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        )
    ]
    condition_ids = [
        ConditionId(id="4e6a6025-b056-4040-b15a-7856a66e1bb6", rule_group_id="db16af99-4a75-4780-8bb0-56fb0a2931a3"),
        ConditionId(id="4d7fe0c2-9ea3-4ddb-b460-03d5a84163f6", rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "c4d96230-bb08-4aab-b63e-48191c472605.field": UUID("0362e67a-b95c-4d2e-94cb-0d748605e184")
    }
    port_displays = {
        ConditionalNode1.Ports.branch_1: PortDisplayOverrides(id=UUID("1eca0f4d-7182-4b2e-873b-4030019a8bbd")),
        ConditionalNode1.Ports.branch_2: PortDisplayOverrides(id=UUID("0c290732-913b-4490-a3bd-e43c23bbace4")),
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2130, y=435), width=None, height=None)
