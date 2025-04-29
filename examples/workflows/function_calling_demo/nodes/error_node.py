from vellum import VellumError
from vellum.workflows.nodes.displayable import ErrorNode as BaseErrorNode


class ErrorNode(BaseErrorNode):
    error = VellumError(message="Unrecognized function call", code="USER_DEFINED_ERROR")
