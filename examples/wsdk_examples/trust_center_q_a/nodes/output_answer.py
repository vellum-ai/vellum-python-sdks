from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .answer_question import AnswerQuestion


class OutputAnswer(FinalOutputNode[BaseState, str]):
    """Finally, we output the model's response to the user's question. This is the value we would use in our application when we ultimately display a response to the user and add it to the Chat History."""

    class Outputs(FinalOutputNode.Outputs):
        value = AnswerQuestion.Outputs.text
