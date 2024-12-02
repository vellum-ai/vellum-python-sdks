from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.conditional_node import ConditionalNode


class ConditionalNodeDisplay(BaseConditionalNodeDisplay[ConditionalNode]):
    label = "Conditional Node"
    node_id = UUID("903aa4b9-70b6-4d32-a12e-488926403836")
    target_handle_id = UUID("91f3cff9-32b8-4cda-aae3-a2c69b9bf650")
    source_handle_ids = {
        0: UUID("d4f0db7d-b04a-4c4d-b9d3-aa3eb61fa3a2"),
        1: UUID("d3489082-f03f-4121-ae60-877fd361c5fe"),
        2: UUID("a913cb88-261b-4fa8-9915-d215e19749ee"),
        3: UUID("fec240f8-8baf-40f9-87e7-f268bff4ed94"),
    }
    rule_ids = [
        RuleIdMap(
            id=UUID("c18a30e5-038a-450d-a2c9-5e385aecb2e5"),
            lhs=RuleIdMap(
                id=UUID("2690b2e3-0384-457d-864c-7d22fbd3def5"),
                lhs=None,
                rhs=None,
                field_node_input_id=UUID("e50c08a5-35db-4415-9fa2-40d0d36a16b2"),
                value_node_input_id=UUID("bf5d2644-7159-4fd7-b0f0-703075645e44"),
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        ),
        RuleIdMap(
            id=UUID("b20bfb89-cb0b-4a17-9135-c0bd3206173b"),
            lhs=RuleIdMap(
                id=UUID("60b216e7-9999-4e1d-bce9-0050f29538e1"),
                lhs=None,
                rhs=None,
                field_node_input_id=UUID("c3175b80-ba17-4adf-9f51-3d45daff1464"),
                value_node_input_id=UUID("2403091a-f4c6-42e4-9a97-0a05c184653f"),
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        ),
        RuleIdMap(
            id=UUID("c321e3d0-e6ee-437b-8860-fc1af277d01b"),
            lhs=RuleIdMap(
                id=UUID("d8e94b2f-e9b5-484c-bd0c-a388747153b9"),
                lhs=None,
                rhs=None,
                field_node_input_id=UUID("e4aa9f5b-9934-4f58-9611-0c1c767bae9b"),
                value_node_input_id=UUID("2398764a-060b-4ee9-9531-60e06b2c95b9"),
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        ),
    ]
    condition_ids = [
        ConditionId(
            id=UUID("4188bda5-5c07-490e-9e17-7e1df1e4fb3a"), rule_group_id=UUID("c18a30e5-038a-450d-a2c9-5e385aecb2e5")
        ),
        ConditionId(
            id=UUID("e2815ae8-9b09-47e3-bd3f-5f17c9d96a31"), rule_group_id=UUID("b20bfb89-cb0b-4a17-9135-c0bd3206173b")
        ),
        ConditionId(
            id=UUID("9be476a3-5757-4faa-b3a6-8383924946f0"), rule_group_id=UUID("c321e3d0-e6ee-437b-8860-fc1af277d01b")
        ),
        ConditionId(id=UUID("8a38731c-a4e8-4f1d-a4a3-8419119294f6"), rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "e23d8319-e907-41e2-ad95-2be4e6aafbb3.field": UUID("e50c08a5-35db-4415-9fa2-40d0d36a16b2"),
        "e23d8319-e907-41e2-ad95-2be4e6aafbb3.value": UUID("bf5d2644-7159-4fd7-b0f0-703075645e44"),
        "60b216e7-9999-4e1d-bce9-0050f29538e1.field": UUID("c3175b80-ba17-4adf-9f51-3d45daff1464"),
        "60b216e7-9999-4e1d-bce9-0050f29538e1.value": UUID("2403091a-f4c6-42e4-9a97-0a05c184653f"),
        "d8e94b2f-e9b5-484c-bd0c-a388747153b9.field": UUID("e4aa9f5b-9934-4f58-9611-0c1c767bae9b"),
        "d8e94b2f-e9b5-484c-bd0c-a388747153b9.value": UUID("2398764a-060b-4ee9-9531-60e06b2c95b9"),
    }
    port_displays = {
        ConditionalNode.Ports.branch_8: PortDisplayOverrides(id=UUID("d4f0db7d-b04a-4c4d-b9d3-aa3eb61fa3a2")),
        ConditionalNode.Ports.branch_9: PortDisplayOverrides(id=UUID("d3489082-f03f-4121-ae60-877fd361c5fe")),
        ConditionalNode.Ports.branch_10: PortDisplayOverrides(id=UUID("a913cb88-261b-4fa8-9915-d215e19749ee")),
        ConditionalNode.Ports.branch_11: PortDisplayOverrides(id=UUID("fec240f8-8baf-40f9-87e7-f268bff4ed94")),
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2084.4413934539916, y=503.21512629358983), width=480, height=283
    )
