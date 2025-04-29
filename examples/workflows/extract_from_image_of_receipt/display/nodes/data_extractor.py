from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay, BaseTryNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.data_extractor import DataExtractor


@BaseTryNodeDisplay.wrap(
    node_id=UUID("39d4d8a9-61c3-49cf-9fb4-0f8c2814a981"), error_output_id=UUID("39d4d8a9-61c3-49cf-9fb4-0f8c2814a981")
)
class DataExtractorDisplay(BaseInlinePromptNodeDisplay[DataExtractor]):
    label = "Data Extractor"
    node_id = UUID("34996c9d-9b6c-41bf-a269-e7984093826b")
    output_id = UUID("da7cf2f7-a4d8-4c06-b1d3-1ca570d88242")
    array_output_id = UUID("acf1ba94-a2bb-462c-a770-0971cace33d0")
    target_handle_id = UUID("87b983b6-7a38-402d-8ce6-a08afc0260f0")
    node_input_ids_by_name = {"chat_history": UUID("462722d6-8acd-4446-b744-28631516e3ee")}
    output_display = {
        DataExtractor.Outputs.text: NodeOutputDisplay(id=UUID("da7cf2f7-a4d8-4c06-b1d3-1ca570d88242"), name="text"),
        DataExtractor.Outputs.results: NodeOutputDisplay(
            id=UUID("acf1ba94-a2bb-462c-a770-0971cace33d0"), name="results"
        ),
        DataExtractor.Outputs.json: NodeOutputDisplay(id=UUID("797fd7b7-d61e-45d4-a80b-8d13f603c78d"), name="json"),
    }
    port_displays = {DataExtractor.Ports.default: PortDisplayOverrides(id=UUID("83d895c9-2203-4b70-95e6-ade11602a39a"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=857.2886057113042, y=-157.99381186416284), width=480, height=175
    )
