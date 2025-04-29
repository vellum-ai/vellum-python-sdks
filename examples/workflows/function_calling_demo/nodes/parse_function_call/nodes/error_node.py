from vellum.workflows.nodes.displayable import ErrorNode

from .error_message import ErrorMessage


class ErrorNode1(ErrorNode):
    error = ErrorMessage.Outputs.result
