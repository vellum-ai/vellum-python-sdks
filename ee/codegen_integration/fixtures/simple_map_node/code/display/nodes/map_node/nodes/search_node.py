from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseSearchNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.map_node.nodes.search_node import SearchNode


class SearchNodeDisplay(BaseSearchNodeDisplay[SearchNode]):
    label = "Search Node"
    node_id = UUID("4b0a7578-e5ec-4d72-b396-62abdecbd101")
    target_handle_id = UUID("df39e340-f66c-4f1c-b030-5437a2183414")
    node_input_ids_by_name = {
        "query": UUID("eca53704-291f-419b-b69e-44ccb9791227"),
        "document_index_id": UUID("f5bdc71b-c100-4237-999f-14b97378da4d"),
        "weights": UUID("0e87177f-287f-459e-90a4-5037cf19e4dc"),
        "limit": UUID("95634b1a-862c-497f-a8d0-b3f10fd6bb76"),
        "separator": UUID("6a35c6d4-2d9f-4409-9313-723970561378"),
        "result_merging_enabled": UUID("ab4c55ed-31bb-46a0-8130-ce291bb89e0e"),
        "external_id_filters": UUID("f891d5bb-fb07-4038-92a9-7f8322f38742"),
        "metadata_filters": UUID("349dbcb2-a58a-46c7-8c61-c720aa9bca40"),
    }
    output_display = {
        SearchNode.Outputs.results: NodeOutputDisplay(id=UUID("8c06f794-38e3-42f0-b68f-d865e50f4f0a"), name="results"),
        SearchNode.Outputs.text: NodeOutputDisplay(id=UUID("503aa2c1-6b99-43e8-98f7-1fef458a8d29"), name="text"),
    }
    port_displays = {SearchNode.Ports.default: PortDisplayOverrides(id=UUID("7c8b42ff-7a21-4011-bf7b-44e06a5eb4c5"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1909.9521341463415, y=212.0475201437282), z_index=None, width=480, height=180
    )
