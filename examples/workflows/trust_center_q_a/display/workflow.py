from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..inputs import Inputs
from ..nodes.answer_question import AnswerQuestion
from ..nodes.formatted_search_results import FormattedSearchResults
from ..nodes.most_recent_message import MostRecentMessage
from ..nodes.output_answer import OutputAnswer
from ..nodes.output_search_results import OutputSearchResults
from ..nodes.output_user_question import OutputUserQuestion
from ..nodes.search_results import SearchResults
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("eeb618e0-2b37-4fa0-933a-cd2c9ae73c25"),
        entrypoint_node_source_handle_id=UUID("93d0da15-cfd4-47ec-9f16-b9f8e2bcfb28"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=1545, y=330), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1046.5185694818517, y=52.289078412761114, zoom=0.4747854734853663)
        ),
    )
    inputs_display = {
        Inputs.chat_history: WorkflowInputsDisplay(id=UUID("499159eb-4f31-4659-9c87-4ad6a727419a"), name="chat_history")
    }
    entrypoint_displays = {
        MostRecentMessage: EntrypointDisplay(
            id=UUID("eeb618e0-2b37-4fa0-933a-cd2c9ae73c25"),
            edge_display=EdgeDisplay(id=UUID("541590a7-c64b-4ec0-bca3-8b2a80f7dfd2")),
        )
    }
    edge_displays = {
        (MostRecentMessage.Ports.default, SearchResults): EdgeDisplay(id=UUID("3742b578-1514-48e4-a21c-f03f48ab2fce")),
        (SearchResults.Ports.default, FormattedSearchResults): EdgeDisplay(
            id=UUID("5d17d921-a0e7-4482-94a0-887817bf26da")
        ),
        (MostRecentMessage.Ports.default, OutputUserQuestion): EdgeDisplay(
            id=UUID("0b71f497-5a13-4080-9961-f21d2929bebf")
        ),
        (SearchResults.Ports.default, OutputSearchResults): EdgeDisplay(
            id=UUID("fdd7afb7-e683-46d4-a4ed-bc478cecebf8")
        ),
        (FormattedSearchResults.Ports.default, AnswerQuestion): EdgeDisplay(
            id=UUID("039f9b34-80f9-4f8d-8d13-2fbb64efb5d3")
        ),
        (AnswerQuestion.Ports.default, OutputAnswer): EdgeDisplay(id=UUID("c54dae0d-a84a-4f82-94b5-072144cec345")),
    }
    output_displays = {
        Workflow.Outputs.search_results: WorkflowOutputDisplay(
            id=UUID("3f526b86-e419-4c89-b7fa-beacd0055556"), name="search_results"
        ),
        Workflow.Outputs.question: WorkflowOutputDisplay(
            id=UUID("c2fb17c7-f6aa-44b0-a4f1-805f46e058c9"), name="question"
        ),
        Workflow.Outputs.answer: WorkflowOutputDisplay(id=UUID("519d3b9b-4caa-4928-abd1-ce3130caabee"), name="answer"),
    }
