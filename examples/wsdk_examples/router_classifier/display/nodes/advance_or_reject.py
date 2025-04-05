from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap

from ...nodes.advance_or_reject import AdvanceOrReject


class AdvanceOrRejectDisplay(BaseConditionalNodeDisplay[AdvanceOrReject]):
    label = "Advance or Reject?"
    node_id = UUID("f08c616c-8581-4b2a-9fe1-53e947d6fd98")
    target_handle_id = UUID("2eac0701-3d89-436d-b348-b9db735cc9f6")
    source_handle_ids = {
        0: UUID("22add5ef-53e9-474d-9b43-81d561578a38"),
        1: UUID("67b02f94-a45e-4328-b838-da2b221a7028"),
    }
    rule_ids = [
        RuleIdMap(
            id="4034307f-1f72-4c89-a8a4-ed26678df519",
            lhs=RuleIdMap(
                id="0520e53d-77a2-4655-96c0-707deee949fb",
                lhs=None,
                rhs=None,
                field_node_input_id="7e2b9caf-a593-436e-80ed-d65fb4a6b321",
                value_node_input_id="52a2a3c8-e60d-49fa-8d76-973d3664422c",
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        )
    ]
    condition_ids = [
        ConditionId(id="f862fe38-f3cf-4298-a354-cda42c3be2c0", rule_group_id="4034307f-1f72-4c89-a8a4-ed26678df519"),
        ConditionId(id="62fbd66c-2624-4652-aaf5-1c1ca17e3b18", rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "9949dfe6-605a-4c1a-9642-37c7382d9658.field": UUID("7e2b9caf-a593-436e-80ed-d65fb4a6b321"),
        "9949dfe6-605a-4c1a-9642-37c7382d9658.value": UUID("52a2a3c8-e60d-49fa-8d76-973d3664422c"),
    }
    port_displays = {
        AdvanceOrReject.Ports.branch_1: PortDisplayOverrides(id=UUID("22add5ef-53e9-474d-9b43-81d561578a38")),
        AdvanceOrReject.Ports.branch_2: PortDisplayOverrides(id=UUID("67b02f94-a45e-4328-b838-da2b221a7028")),
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=1463.5, y=1263), width=448, height=185)
