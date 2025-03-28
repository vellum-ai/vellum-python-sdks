from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.get_search_results_with_metadata import GetSearchResultsWithMetadata


class GetSearchResultsWithMetadataDisplay(BaseTemplatingNodeDisplay[GetSearchResultsWithMetadata]):
    label = "Get Search Results With Metadata"
    node_id = UUID("55846c99-4741-42db-8c04-366efcec3d93")
    target_handle_id = UUID("9023b50f-5341-477b-b15c-0fafa3aa3376")
    node_input_ids_by_name = {
        "inputs.docs_context": UUID("c9c60844-6d7d-45a0-b20f-ef174600d04f"),
        "template": UUID("8ee889d8-2f4a-40b9-85ae-1d1df6fbb950"),
    }
    output_display = {
        GetSearchResultsWithMetadata.Outputs.result: NodeOutputDisplay(
            id=UUID("bdb5a5c0-2659-4e15-8f04-fb86189e8e13"), name="result"
        )
    }
    port_displays = {
        GetSearchResultsWithMetadata.Ports.default: PortDisplayOverrides(
            id=UUID("8e06408e-6e40-48a4-832f-1b403a4e64e1")
        )
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3405, y=1665), width=460, height=229)
