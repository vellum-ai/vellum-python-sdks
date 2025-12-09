from vellum.workflows.nodes.displayable import FinalOutputNode

from ..state import State


class FinalOutput(FinalOutputNode[State, list]):
    class Outputs(FinalOutputNode.Outputs):
        # Return the full chat history so callers can observe persistence across executions
        value = State.chat_history
