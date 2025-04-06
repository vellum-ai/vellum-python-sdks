from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay

from ...nodes.output_search_results import OutputSearchResults


class OutputSearchResultsDisplay(BaseFinalOutputNodeDisplay[OutputSearchResults]):
    label = "Output: Search Results"
    node_id = UUID("11a597f3-6655-47d5-9e79-ebb3c11965d1")
    target_handle_id = UUID("8ebe1a2e-3971-4b1a-9605-2b6a8c59d134")
    output_id = UUID("3f526b86-e419-4c89-b7fa-beacd0055556")
    output_name = "search_results"
    node_input_id = UUID("c4e72fc2-fa5b-47fd-849c-a5bddf738558")
    node_input_ids_by_name = {"node_input": UUID("c4e72fc2-fa5b-47fd-849c-a5bddf738558")}
    output_display = {
        OutputSearchResults.Outputs.value: NodeOutputDisplay(
            id=UUID("3f526b86-e419-4c89-b7fa-beacd0055556"), name="value"
        )
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=2991.452657958532, y=-177.54047446589146), width=447, height=239
    )
