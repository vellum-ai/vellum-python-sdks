from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseSearchNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.q_a_bank_lookup import QABankLookup


class QABankLookupDisplay(BaseSearchNodeDisplay[QABankLookup]):
    label = "Q&A Bank Lookup"
    node_id = UUID("4193098f-9b91-4e69-8cdf-302c7cfe3648")
    target_handle_id = UUID("5dc53a6f-8617-4898-b983-53a2964a049a")
    metadata_filter_input_id_by_operand_id = {}
    node_input_ids_by_name = {
        "query": UUID("c660f5de-2bd7-451b-a5e8-d17d51670f76"),
        "document_index_id": UUID("e43d1e7b-9d36-4a88-8fab-98ec8d725e42"),
        "weights": UUID("dcc44135-4496-4f06-bf55-f9ead9506c9c"),
        "limit": UUID("63f5af38-7360-4395-b765-b64c9d9ee4c8"),
        "separator": UUID("a4ba6b24-f6c8-45ad-bf95-0b67e604f845"),
        "result_merging_enabled": UUID("d65ce831-6a66-44eb-bc84-1c4c0bc3e640"),
        "external_id_filters": UUID("d24be36b-f3b3-46aa-8a7c-b465d70661a7"),
        "metadata_filters": UUID("f84a6937-d464-4028-8e43-ed5aaa11cf92"),
    }
    output_display = {
        QABankLookup.Outputs.results: NodeOutputDisplay(
            id=UUID("0194b94a-b0b9-419d-a67b-d4056dc7668a"), name="results"
        ),
        QABankLookup.Outputs.text: NodeOutputDisplay(id=UUID("35fd1b25-4dba-40a1-af90-809f1094e13b"), name="text"),
    }
    port_displays = {QABankLookup.Ports.default: PortDisplayOverrides(id=UUID("c683f976-b555-4f7f-90f9-2c5c81ede842"))}
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=2625, y=675), width=480, height=185)
