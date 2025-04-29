from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseConditionalNodeDisplay
from vellum_ee.workflows.display.nodes.types import PortDisplayOverrides
from vellum_ee.workflows.display.nodes.vellum.conditional_node import ConditionId, RuleIdMap

from ...nodes.needs_revision import NeedsRevision


class NeedsRevisionDisplay(BaseConditionalNodeDisplay[NeedsRevision]):
    label = "Needs Revision?"
    node_id = UUID("bbe4360f-483a-4bca-a6e3-308ab9defca1")
    target_handle_id = UUID("f1ca3986-79d5-4978-9301-d1e2134b76eb")
    source_handle_ids = {
        0: UUID("785b5a45-4fad-4dcf-9d58-523a1a5a7f07"),
        1: UUID("d164277c-30d6-4a01-ad25-a5f52100f5e4"),
        2: UUID("1b8f421a-ce0a-4f6a-95b2-a5d3322fd270"),
    }
    rule_ids = [
        RuleIdMap(
            id="ae3f9a87-56db-4654-9036-b04227bc36ec",
            lhs=RuleIdMap(
                id="3f392937-2a4f-4177-8725-87922bd63abb",
                lhs=None,
                rhs=None,
                field_node_input_id="53181c75-b01c-4a21-b294-de468f41e323",
                value_node_input_id="36c7abeb-cd2c-461a-8ced-29b332523d98",
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        ),
        RuleIdMap(
            id="a8131318-40cb-4564-a4e8-9673bbab92bc",
            lhs=RuleIdMap(
                id="1b8dc712-6575-4771-99cf-e713082b490d",
                lhs=None,
                rhs=None,
                field_node_input_id="f64631c4-22ee-4a1e-81c4-0d6038bcdfed",
                value_node_input_id="27a75c26-39af-45bc-8e85-e77bc487d896",
            ),
            rhs=None,
            field_node_input_id=None,
            value_node_input_id=None,
        ),
    ]
    condition_ids = [
        ConditionId(id="eb1068af-9191-478f-b569-90143e413027", rule_group_id="ae3f9a87-56db-4654-9036-b04227bc36ec"),
        ConditionId(id="c43bcb6d-ec50-44ed-8901-c70ab043ab07", rule_group_id="a8131318-40cb-4564-a4e8-9673bbab92bc"),
        ConditionId(id="1852f92a-e668-4b87-850f-ef1e3cb7e5b3", rule_group_id=None),
    ]
    node_input_ids_by_name = {
        "5b8a9b60-cfbe-41ab-8cb5-87d4c7570ed9.field": UUID("53181c75-b01c-4a21-b294-de468f41e323"),
        "5b8a9b60-cfbe-41ab-8cb5-87d4c7570ed9.value": UUID("36c7abeb-cd2c-461a-8ced-29b332523d98"),
        "2a4871e2-37bc-4114-8888-f2ebe0ee43e9.field": UUID("f64631c4-22ee-4a1e-81c4-0d6038bcdfed"),
        "2a4871e2-37bc-4114-8888-f2ebe0ee43e9.value": UUID("27a75c26-39af-45bc-8e85-e77bc487d896"),
    }
    port_displays = {
        NeedsRevision.Ports.branch_1: PortDisplayOverrides(id=UUID("785b5a45-4fad-4dcf-9d58-523a1a5a7f07")),
        NeedsRevision.Ports.branch_2: PortDisplayOverrides(id=UUID("d164277c-30d6-4a01-ad25-a5f52100f5e4")),
        NeedsRevision.Ports.branch_3: PortDisplayOverrides(id=UUID("1b8f421a-ce0a-4f6a-95b2-a5d3322fd270")),
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3656.222715551748, y=279.83299396794433),
        width=455,
        height=325,
        comment=NodeDisplayComment(expanded=True),
    )
