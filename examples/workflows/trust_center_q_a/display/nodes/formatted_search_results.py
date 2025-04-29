from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.formatted_search_results import FormattedSearchResults


class FormattedSearchResultsDisplay(BaseTemplatingNodeDisplay[FormattedSearchResults]):
    label = "Formatted Search Results"
    node_id = UUID("3a762441-4bfa-46ca-a2b0-44c392b4a905")
    target_handle_id = UUID("d0eab722-992c-4917-ab26-ef42599a1ac3")
    node_input_ids_by_name = {
        "inputs.results": UUID("9ab1342b-3f0c-40bc-916b-7307619f25a4"),
        "template": UUID("26ead46f-1f9f-4ada-9a86-9d132a521331"),
    }
    output_display = {
        FormattedSearchResults.Outputs.result: NodeOutputDisplay(
            id=UUID("57af0bae-70a4-4762-b997-6ed6332d4ffe"), name="result"
        )
    }
    port_displays = {
        FormattedSearchResults.Ports.default: PortDisplayOverrides(id=UUID("fea0cc9d-33e6-46e8-9c56-6a3ffb25572c"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2986.241584788271, y=334.6811885912033),
        width=460,
        height=315,
        comment=NodeDisplayComment(expanded=True),
    )
