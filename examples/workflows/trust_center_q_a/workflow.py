from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.answer_question import AnswerQuestion
from .nodes.copy_of_note import CopyOfNote
from .nodes.formatted_search_results import FormattedSearchResults
from .nodes.most_recent_message import MostRecentMessage
from .nodes.output_answer import OutputAnswer
from .nodes.output_search_results import OutputSearchResults
from .nodes.output_user_question import OutputUserQuestion
from .nodes.search_results import SearchResults


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = MostRecentMessage >> {
        SearchResults
        >> {
            FormattedSearchResults >> AnswerQuestion >> OutputAnswer,
            OutputSearchResults,
        },
        OutputUserQuestion,
    }
    unused_graphs = {CopyOfNote}

    class Outputs(BaseWorkflow.Outputs):
        search_results = OutputSearchResults.Outputs.value
        question = OutputUserQuestion.Outputs.value
        answer = OutputAnswer.Outputs.value
