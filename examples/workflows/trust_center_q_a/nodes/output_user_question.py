from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .most_recent_message import MostRecentMessage


class OutputUserQuestion(FinalOutputNode[BaseState, str]):
    """Exposing intermediate outputs can be useful for unit testing individual pieces of the Workflow in the Evaluations tab. For example, by exposing the user's question to our Test Suite, we could use the RAGAS Context Relevancy Metric to evaluate the quality of the search results separately from the quality of the model's final answer."""

    class Outputs(FinalOutputNode.Outputs):
        value = MostRecentMessage.Outputs.result
