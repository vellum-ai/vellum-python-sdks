from vellum.workflows.nodes.displayable import ErrorNode as BaseErrorNode

from ..inputs import Inputs


class ErrorNode(BaseErrorNode):
    error = Inputs.query
