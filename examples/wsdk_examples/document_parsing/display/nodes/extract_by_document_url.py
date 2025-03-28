from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.extract_by_document_url import ExtractByDocumentURL


class ExtractByDocumentURLDisplay(BaseInlinePromptNodeDisplay[ExtractByDocumentURL]):
    label = "Extract by Document URL"
    node_id = UUID("a3ba2912-c0c1-432c-bd1b-a10f65b7649c")
    output_id = UUID("63a1191f-ee4a-4194-8fc9-531d64a1f301")
    array_output_id = UUID("1bae2ae0-7b6b-4a11-bb4c-85e222d3d5dd")
    target_handle_id = UUID("e876d7e8-2023-43d8-a29d-d1c9ed8df541")
    node_input_ids_by_name = {"chat_history": UUID("816d73c4-78b7-46e0-b4fd-2c8fbab4886c")}
    output_display = {
        ExtractByDocumentURL.Outputs.text: NodeOutputDisplay(
            id=UUID("63a1191f-ee4a-4194-8fc9-531d64a1f301"), name="text"
        ),
        ExtractByDocumentURL.Outputs.results: NodeOutputDisplay(
            id=UUID("1bae2ae0-7b6b-4a11-bb4c-85e222d3d5dd"), name="results"
        ),
        ExtractByDocumentURL.Outputs.json: NodeOutputDisplay(
            id=UUID("a8535d1c-bfd7-4454-ba35-1585c883dcbe"), name="json"
        ),
    }
    port_displays = {
        ExtractByDocumentURL.Ports.default: PortDisplayOverrides(id=UUID("a15192cb-c2c3-44ff-8a62-e35ddb65e67d"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=837.4721057480847, y=667.4771042124831), width=480, height=175
    )
