from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.answer_from_help_docs import AnswerFromHelpDocs
from .nodes.answer_from_q_a_database import AnswerFromQADatabase
from .nodes.final_output import FinalOutput
from .nodes.get_search_results_with_metadata import GetSearchResultsWithMetadata
from .nodes.help_docs_lookup import HelpDocsLookup
from .nodes.merge_node import MergeNode
from .nodes.q_a_bank_lookup import QABankLookup
from .nodes.take_best_response import TakeBestResponse


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = (
        {
            QABankLookup >> AnswerFromQADatabase,
            HelpDocsLookup >> GetSearchResultsWithMetadata >> AnswerFromHelpDocs,
        }
        >> MergeNode
        >> TakeBestResponse
        >> FinalOutput
    )

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
