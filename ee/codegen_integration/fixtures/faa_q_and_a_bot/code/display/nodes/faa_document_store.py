from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseSearchNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides
from vellum_ee.workflows.display.vellum import NodeDisplayData, NodeDisplayPosition

from ...nodes.faa_document_store import FAADocumentStore


class FAADocumentStoreDisplay(BaseSearchNodeDisplay[FAADocumentStore]):
    label = "FAA Document Store"
    node_id = UUID("fbe1571c-e904-40f6-a414-55adf3b72817")
    target_handle_id = UUID("32346adc-40f3-49b5-aea8-5c64b88643ef")
    node_input_ids_by_name = {
        "query": UUID("d25dcbce-5d7b-40a4-a5b4-2033bd0d350a"),
        "document_index_id": UUID("43c7c857-8b25-4dd9-ba16-aa2e5e6ecd0a"),
        "weights": UUID("0ad55ab6-dd3f-4490-b2a8-9d3e4bc27c7b"),
        "limit": UUID("165a6791-79d3-45a3-8e47-74b2de3bdc44"),
        "separator": UUID("52c86f14-c9f6-4473-afaf-2d0dd0d8f738"),
        "result_merging_enabled": UUID("b30cd523-f7cd-4fec-ac37-44eda92c2d16"),
        "external_id_filters": UUID("53cbc583-415f-4c1d-920d-76a3875e193d"),
        "metadata_filters": UUID("a7abbcf8-6c16-411d-b2da-da09ec357ca3"),
    }
    output_display = {
        FAADocumentStore.Outputs.results: NodeOutputDisplay(
            id=UUID("564d7f2a-aa8c-4e9a-b93f-24d8f6418aaf"), name="results"
        ),
        FAADocumentStore.Outputs.text: NodeOutputDisplay(id=UUID("2f4b7f20-9161-4dea-bfb3-f6154c675640"), name="text"),
    }
    port_displays = {
        FAADocumentStore.Ports.default: PortDisplayOverrides(id=UUID("0b203edd-ed4c-4593-9e17-deaeb2780e14"))
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=3318, y=271.25), width=452, height=177)
