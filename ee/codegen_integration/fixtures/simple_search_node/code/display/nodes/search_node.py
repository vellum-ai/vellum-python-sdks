from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseSearchNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.search_node import SearchNode


class SearchNodeDisplay(BaseSearchNodeDisplay[SearchNode]):
    target_handle_id = UUID("370d712d-3369-424e-bcf7-f4da1aef3928")
    metadata_filter_input_id_by_operand_id = {
        UUID("a6322ca2-8b65-4d26-b3a1-f926dcada0fa"): UUID("a6322ca2-8b65-4d26-b3a1-f926dcada0fa"),
        UUID("c539a2e2-0873-43b0-ae21-81790bb1c4cb"): UUID("c539a2e2-0873-43b0-ae21-81790bb1c4cb"),
        UUID("a89483b6-6850-4105-8c4e-ec0fd197cd43"): UUID("a89483b6-6850-4105-8c4e-ec0fd197cd43"),
        UUID("847b8ee0-2c37-4e41-9dea-b4ba3579e2c1"): UUID("847b8ee0-2c37-4e41-9dea-b4ba3579e2c1"),
    }
    label = "Search Node"
    node_id = UUID("e5ff9360-a29c-437b-a9c1-05fc52df2834")
    node_input_ids_by_name = {
        "query": UUID("f3a0d8b9-7772-4db6-8e28-f49f8c4d9e2a"),
        "document_index_id": UUID("b49bc1ab-2ad5-4cf2-8966-5cc87949900d"),
        "weights": UUID("1daf3180-4b92-472a-8665-a7703c84a94e"),
        "limit": UUID("161d264e-d04e-4c37-8e50-8bbb4c90c46e"),
        "separator": UUID("4eddefc0-90d5-422a-aec2-bc94c8f1d83c"),
        "result_merging_enabled": UUID("dc9f880b-81bc-4644-b025-8f7d5db23a48"),
        "external_id_filters": UUID("61933e79-b0c2-4e3c-bf07-e2d93b9d9c54"),
        "metadata_filters": UUID("fdc7256f-88ed-4a43-9b85-41c2961a1ac2"),
        "vellum-query-builder-variable-a6322ca2-8b65-4d26-b3a1-f926dcada0fa": UUID(
            "a6322ca2-8b65-4d26-b3a1-f926dcada0fa"
        ),
        "vellum-query-builder-variable-c539a2e2-0873-43b0-ae21-81790bb1c4cb": UUID(
            "c539a2e2-0873-43b0-ae21-81790bb1c4cb"
        ),
        "vellum-query-builder-variable-a89483b6-6850-4105-8c4e-ec0fd197cd43": UUID(
            "a89483b6-6850-4105-8c4e-ec0fd197cd43"
        ),
        "vellum-query-builder-variable-847b8ee0-2c37-4e41-9dea-b4ba3579e2c1": UUID(
            "847b8ee0-2c37-4e41-9dea-b4ba3579e2c1"
        ),
    }
    output_display = {
        SearchNode.Outputs.results: NodeOutputDisplay(id=UUID("77839b3c-fe1c-4dcb-9c61-2fac827f729b"), name="results"),
        SearchNode.Outputs.text: NodeOutputDisplay(id=UUID("d56d7c49-7b45-4933-9779-2bd7f82c2141"), name="text"),
    }
    port_displays = {SearchNode.Ports.default: PortDisplayOverrides(id=UUID("e4dedb66-0638-4f0c-9941-6420bfe353b2"))}
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1966.960664819945, y=223.1684037396122), width=480, height=180
    )
