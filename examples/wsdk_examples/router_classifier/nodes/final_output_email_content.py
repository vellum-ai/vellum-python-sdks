from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .write_next_round_email import WriteNextRoundEmail
from .write_rejection_email import WriteRejectionEmail


class FinalOutputEmailContent(FinalOutputNode[BaseState, str]):
    """Here we use fallback values such that we can use a single Final Output node regardless of which conditional path is taken."""

    class Outputs(FinalOutputNode.Outputs):
        value = WriteNextRoundEmail.Outputs.text.coalesce(WriteRejectionEmail.Outputs.text)
