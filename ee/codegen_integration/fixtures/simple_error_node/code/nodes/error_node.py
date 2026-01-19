from vellum.workflows.nodes.displayable import ErrorNode as BaseErrorNode

from ..inputs import Inputs


class ErrorNode(BaseErrorNode):
    error = Inputs.custom_error

    class Display(BaseErrorNode.Display):
        x = 1966.960664819945
        y = 223.1684037396122
