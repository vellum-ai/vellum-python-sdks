from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseSearchNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.search_results import SearchResults


class SearchResultsDisplay(BaseSearchNodeDisplay[SearchResults]):
    label = "Search Results"
    node_id = UUID("18a3ba39-07d8-4cf1-8c42-4bc3322d6910")
    target_handle_id = UUID("6375f7ea-c1b8-4bca-ba19-0c45bc75831b")
    metadata_filter_input_id_by_operand_id = {}
    node_input_ids_by_name = {
        "query": UUID("3f52de4c-2123-45b6-80d2-0253c42eb87f"),
        "document_index_id": UUID("90d2e8f8-1bcb-4004-b69a-429db4f3e832"),
        "weights": UUID("e3875cf1-7635-4a7a-8dc7-85e4875ff088"),
        "limit": UUID("fd428e38-4a5c-48e5-bcff-0003bdd5ddb9"),
        "separator": UUID("e50fd18a-f335-4ea2-8ab2-e2180cfaba58"),
        "result_merging_enabled": UUID("cd61d622-3053-40e0-8eac-2e00d1a19a81"),
        "external_id_filters": UUID("47506750-227c-469a-9875-18414cdc7379"),
        "metadata_filters": UUID("6086c581-152e-4983-82fa-476511964ef6"),
    }
    output_display = {
        SearchResults.Outputs.results: NodeOutputDisplay(
            id=UUID("3f3d52db-649c-484a-af5f-17986b861a79"), name="results"
        ),
        SearchResults.Outputs.text: NodeOutputDisplay(id=UUID("da7f1722-0986-4313-abb3-d8550f8031d0"), name="text"),
    }
    port_displays = {SearchResults.Ports.default: PortDisplayOverrides(id=UUID("7f634369-dd10-4894-baa9-a73d38732ea8"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2398.232394395274, y=252.2547364643862),
        width=465,
        height=271,
        comment=NodeDisplayComment(expanded=True),
    )
