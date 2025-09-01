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
from ..nodes.answer_from_help_docs import AnswerFromHelpDocs
from ..nodes.answer_from_q_a_database import AnswerFromQADatabase
from ..nodes.final_output import FinalOutput
from ..nodes.get_search_results_with_metadata import GetSearchResultsWithMetadata
from ..nodes.help_docs_lookup import HelpDocsLookup
from ..nodes.merge_node import MergeNode
from ..nodes.q_a_bank_lookup import QABankLookup
from ..nodes.take_best_response import TakeBestResponse
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("2edf6a15-5a45-4662-8c26-76e6c65456dd"),
        entrypoint_node_source_handle_id=UUID("0168427d-ed02-47ba-98c2-e51fb25d6273"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=2235, y=1290), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-2349.500094897242, y=-487.238689370777, zoom=0.577587531707226)
        ),
    )
    inputs_display = {
        Inputs.question: WorkflowInputsDisplay(id=UUID("83be60e4-5d0a-43e4-99fc-691e2fb623f6"), name="question")
    }
    entrypoint_displays = {
        QABankLookup: EntrypointDisplay(
            id=UUID("2edf6a15-5a45-4662-8c26-76e6c65456dd"),
            edge_display=EdgeDisplay(id=UUID("139d2454-ed41-4e6f-9141-4e1e7441ef09")),
        ),
        HelpDocsLookup: EntrypointDisplay(
            id=UUID("2edf6a15-5a45-4662-8c26-76e6c65456dd"),
            edge_display=EdgeDisplay(id=UUID("bcb98193-5019-4e04-86b5-7b76ac7530b2")),
        ),
    }
    edge_displays = {
        (HelpDocsLookup.Ports.default, GetSearchResultsWithMetadata): EdgeDisplay(
            id=UUID("40c24a06-52fb-4381-8c63-0ce40a741f30")
        ),
        (QABankLookup.Ports.default, AnswerFromQADatabase): EdgeDisplay(
            id=UUID("c98536b9-fac3-4ea1-b495-fd5429888a2d")
        ),
        (AnswerFromQADatabase.Ports.default, MergeNode): EdgeDisplay(id=UUID("bd6e3401-f0d3-421e-a522-ff63c8029bd8")),
        (GetSearchResultsWithMetadata.Ports.default, AnswerFromHelpDocs): EdgeDisplay(
            id=UUID("8fd447f0-300b-4378-9c4b-3e1b38fd4476")
        ),
        (AnswerFromHelpDocs.Ports.default, MergeNode): EdgeDisplay(id=UUID("68fa5245-7c8d-4cb6-b8d8-1cff712cb994")),
        (MergeNode.Ports.default, TakeBestResponse): EdgeDisplay(id=UUID("a9a1c676-480c-472b-9f7b-3366e1b7a1fd")),
        (TakeBestResponse.Ports.default, FinalOutput): EdgeDisplay(id=UUID("a83ce9d1-8074-4963-8838-885d683afde3")),
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("e15f7fa4-cb16-4a38-8a8b-75ee6e77a95e"), name="final-output"
        )
    }
