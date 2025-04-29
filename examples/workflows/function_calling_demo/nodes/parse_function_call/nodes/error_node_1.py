from vellum import VellumError
from vellum.workflows.nodes.displayable import ErrorNode


class ErrorNode2(ErrorNode):
    error = VellumError(message="No function call found.", code="USER_DEFINED_ERROR")
