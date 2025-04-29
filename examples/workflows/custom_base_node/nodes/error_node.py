from vellum.workflows.nodes.displayable import ErrorNode as BaseErrorNode


class ErrorNode(BaseErrorNode):
    error = "Unexpected function call name from the model."
