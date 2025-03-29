from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseSearchNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.help_docs_lookup import HelpDocsLookup


class HelpDocsLookupDisplay(BaseSearchNodeDisplay[HelpDocsLookup]):
    label = "Help Docs Lookup"
    node_id = UUID("7128dc10-b8ab-4fc2-b363-6ea9ab58e1b5")
    target_handle_id = UUID("e9cafff7-a5ce-4afc-befe-9da250a8ac3e")
    metadata_filter_input_id_by_operand_id = {}
    node_input_ids_by_name = {
        "query": UUID("16d6a7df-b431-413d-ae5e-483c0c772935"),
        "document_index_id": UUID("f756c5ca-4571-4325-9732-b081b9a9b1ae"),
        "weights": UUID("b049bec5-cadd-4842-a662-eaaa7cf6a80a"),
        "limit": UUID("92fb873b-af59-4043-ab80-27fb1947e7d6"),
        "separator": UUID("57bca8d9-4b25-4c0b-94df-8ae5e98b35d1"),
        "result_merging_enabled": UUID("3068e8f7-1dc5-48ea-91af-03e6d16495a0"),
        "external_id_filters": UUID("41bc7ad7-a2e9-4dc7-b00a-673cb5b80b09"),
        "metadata_filters": UUID("56ea3c07-b224-463e-99a5-d62e510d87c9"),
    }
    output_display = {
        HelpDocsLookup.Outputs.results: NodeOutputDisplay(
            id=UUID("d3062655-bcf9-4074-b037-6bc544cfd0ab"), name="results"
        ),
        HelpDocsLookup.Outputs.text: NodeOutputDisplay(id=UUID("b1c8e591-1576-4146-ad8a-fc082eabfd7c"), name="text"),
    }
    port_displays = {
        HelpDocsLookup.Ports.default: PortDisplayOverrides(id=UUID("13d97aad-78fd-4d79-ac9e-b0c944777716"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2610, y=1545), width=480, height=185)
