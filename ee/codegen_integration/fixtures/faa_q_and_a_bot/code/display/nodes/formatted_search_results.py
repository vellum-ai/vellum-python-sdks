from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseTemplatingNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.formatted_search_results import FormattedSearchResults


class FormattedSearchResultsDisplay(BaseTemplatingNodeDisplay[FormattedSearchResults]):
    label = "Formatted Search Results"
    node_id = UUID("5e23510e-ef40-4ee1-99ed-0e03f1796cfa")
    target_handle_id = UUID("815664ad-b42f-40ea-9607-b23643a224a8")
    node_input_ids_by_name = {
        "template": UUID("757a3546-7757-45c9-b0e8-2cc813254285"),
        "inputs.results": UUID("7bce9418-f01e-4873-bd4c-d1d5b4340afb"),
    }
    output_display = {
        FormattedSearchResults.Outputs.result: NodeOutputDisplay(
            id=UUID("8b8543d8-7b70-4345-9802-76fcedb7b651"), name="result"
        )
    }
    port_displays = {
        FormattedSearchResults.Ports.default: PortDisplayOverrides(id=UUID("886d79d2-2a97-4c15-8172-e9a157c9090d"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3923.3878883718644, y=-458.89620665696896), width=454, height=221, z_index=None
    )
