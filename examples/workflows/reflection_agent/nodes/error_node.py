from vellum.workflows.nodes.displayable import ErrorNode as BaseErrorNode


class ErrorNode(BaseErrorNode):
    error = "Failed to solve problem in given number of attempts"
