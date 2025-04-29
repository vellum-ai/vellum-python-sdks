from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.answer_from_q_a_database import AnswerFromQADatabase


class AnswerFromQADatabaseDisplay(BaseInlinePromptNodeDisplay[AnswerFromQADatabase]):
    label = "Answer from Q&A Database"
    node_id = UUID("19e33306-0838-4ce7-8c5d-e9d3c3f7b651")
    output_id = UUID("507144b2-1fa7-4dc9-807b-1ac5d3e8222f")
    array_output_id = UUID("12d21eb9-8e69-43fc-9a85-7862772cfe96")
    target_handle_id = UUID("32491208-05df-4c63-9d78-9e5590fc7962")
    node_input_ids_by_name = {
        "context_str": UUID("df01e4d5-724e-46bd-95a2-8814f8d73d24"),
        "customer_question": UUID("55ce3cc9-388d-4aff-a68e-db69ab350e3a"),
    }
    output_display = {
        AnswerFromQADatabase.Outputs.text: NodeOutputDisplay(
            id=UUID("507144b2-1fa7-4dc9-807b-1ac5d3e8222f"), name="text"
        ),
        AnswerFromQADatabase.Outputs.results: NodeOutputDisplay(
            id=UUID("12d21eb9-8e69-43fc-9a85-7862772cfe96"), name="results"
        ),
        AnswerFromQADatabase.Outputs.json: NodeOutputDisplay(
            id=UUID("6f9e3b26-5d94-493c-b682-cf63d00c10c6"), name="json"
        ),
    }
    port_displays = {
        AnswerFromQADatabase.Ports.default: PortDisplayOverrides(id=UUID("7d4f2c1c-7ddb-4a8d-9956-699d6823b4a7"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=3276.4025292273127, y=655.8411695053666), width=480, height=229
    )
