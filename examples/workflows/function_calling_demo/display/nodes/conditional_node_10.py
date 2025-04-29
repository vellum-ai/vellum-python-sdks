from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap

from ...nodes.conditional_node_10 import ConditionalNode10


class ConditionalNode10Display(BaseConditionalNodeDisplay[ConditionalNode10]):
    label = "Conditional Node 10"
    node_id = UUID("3ab8c006-2d4e-4025-b39d-314ac549afd6")
    target_handle_id = UUID("a5a91252-cd98-44d9-a19e-683bd8da7d01")
    source_handle_ids = {
        0: UUID("cb376fec-4053-4ecc-8acd-118ac972b393"),
        1: UUID("ca10ed22-f23f-4a50-ac36-a64877d13b9c"),
    }
    rule_ids = [
        RuleIdMap(
            id="c125682f-b736-40fa-a9e2-bfafcbc2312b",
            lhs=RuleIdMap(
                id="d0a1fbec-f2f9-4c3a-9756-9865e92d41fe",
                lhs=None,
                rhs=None,
                field_node_input_id="fc26c9a7-f514-4bdb-93b4-374fd6272afc",
                value_node_input_id="42d853d9-dcd0-4309-baed-4f74317e778c",
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        )
    ]
    condition_ids = [
        ConditionId(id="777fa95e-3442-4f46-83f2-c1ff8b609ec9", rule_group_id="c125682f-b736-40fa-a9e2-bfafcbc2312b"),
        ConditionId(id="89ea5a9b-2330-46dc-a075-04c8608bc0c1", rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "b946ebf5-6865-4f84-a08e-9bb1ed2867df.field": UUID("fc26c9a7-f514-4bdb-93b4-374fd6272afc"),
        "b946ebf5-6865-4f84-a08e-9bb1ed2867df.value": UUID("42d853d9-dcd0-4309-baed-4f74317e778c"),
    }
    port_displays = {
        ConditionalNode10.Ports.branch_1: PortDisplayOverrides(id=UUID("cb376fec-4053-4ecc-8acd-118ac972b393")),
        ConditionalNode10.Ports.branch_2: PortDisplayOverrides(id=UUID("ca10ed22-f23f-4a50-ac36-a64877d13b9c")),
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2156.6652061538634, y=240), width=460, height=177)
