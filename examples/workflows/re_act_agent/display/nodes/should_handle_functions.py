from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap

from ...nodes.should_handle_functions import ShouldHandleFunctions


class ShouldHandleFunctionsDisplay(BaseConditionalNodeDisplay[ShouldHandleFunctions]):
    label = "Should Handle Functions?"
    node_id = UUID("fc97e935-dbeb-47c3-81ec-429396f8ffd2")
    target_handle_id = UUID("4ce430b1-e9a7-4147-b2db-35a90f63c2ce")
    source_handle_ids = {
        0: UUID("b8533e34-12c9-4b69-bd38-b99a42704724"),
        1: UUID("689c9fd4-4d6f-4140-b3cf-d1254561034a"),
    }
    rule_ids = [
        RuleIdMap(
            id="b57b9d43-9804-47bc-aa4d-b8c8d59fa2b0",
            lhs=RuleIdMap(
                id="3e1cc848-6a85-4e13-aad4-431b0ce1094d",
                lhs=None,
                rhs=None,
                field_node_input_id="479816da-4919-40ba-aeca-09fa751bb320",
                value_node_input_id="19aa9598-8fdf-4f49-830a-9288b4871f16",
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        )
    ]
    condition_ids = [
        ConditionId(id="53a6356f-ddc7-44a4-be78-7f1e28401da7", rule_group_id="b57b9d43-9804-47bc-aa4d-b8c8d59fa2b0"),
        ConditionId(id="bdb467e5-3e36-4613-9b9f-884a2133b939", rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "de990b44-3c5f-44bc-8867-52ee16471a47.field": UUID("479816da-4919-40ba-aeca-09fa751bb320"),
        "de990b44-3c5f-44bc-8867-52ee16471a47.value": UUID("19aa9598-8fdf-4f49-830a-9288b4871f16"),
    }
    port_displays = {
        ShouldHandleFunctions.Ports.branch_1: PortDisplayOverrides(id=UUID("b8533e34-12c9-4b69-bd38-b99a42704724")),
        ShouldHandleFunctions.Ports.branch_2: PortDisplayOverrides(id=UUID("689c9fd4-4d6f-4140-b3cf-d1254561034a")),
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2132.186427579077, y=-17.02717503525355), width=448, height=185
    )
