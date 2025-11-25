from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseSearchNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from .....nodes.subworkflow_node.nodes.search_node import SearchNode


class SearchNodeDisplay(BaseSearchNodeDisplay[SearchNode]):
    node_id = UUID("e413adc6-40f8-4772-8b28-769954d68d26")
    target_handle_id = UUID("d2e2e4e4-a2a4-4a5d-a8fa-d51a1f9d9818")
    node_input_ids_by_name = {
        "query": UUID("73c73ee1-3310-4376-8546-86c13de8ff15"),
        "document_index_id": UUID("eb40b4bd-2fe8-4f8b-868f-494679952220"),
        "weights": UUID("efd608f3-75bb-49b4-9f73-10ef9d63248f"),
        "limit": UUID("c923342a-eb17-4adf-a75a-a709c0ac9574"),
        "separator": UUID("1de070ea-7492-441f-bce0-52a482d8f6e4"),
        "result_merging_enabled": UUID("748343a7-241b-47b0-a1bc-4a27ef14c217"),
        "external_id_filters": UUID("428646ee-a21b-4f1f-807b-4b00f680ada7"),
        "metadata_filters": UUID("a46d1abc-f47e-4aee-b11b-196baa5273be"),
    }
    output_display = {
        SearchNode.Outputs.results: NodeOutputDisplay(id=UUID("d3ed4bc8-8753-4dd1-bdbd-20d7f5919c31"), name="results"),
        SearchNode.Outputs.text: NodeOutputDisplay(id=UUID("240f117b-f47f-4cdf-8c1d-b5fba7f71310"), name="text"),
    }
    port_displays = {SearchNode.Ports.default: PortDisplayOverrides(id=UUID("b2c00256-11db-43e4-9282-8f0265f72650"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2053.3811695404584, y=240.84267524293904), width=480, height=179
    )
