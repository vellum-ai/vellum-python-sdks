from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .create_linear_ticket_node import CreateLinearTicketNode


class OutputLinearTicket(FinalOutputNode[BaseState, str]):
    """Returns the Linear ticket URL as workflow output."""

    class Outputs(FinalOutputNode.Outputs):
        value = CreateLinearTicketNode.Outputs.text
