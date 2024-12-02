from vellum.workflows.nodes.bases.base import BaseNode

from ..inputs import Inputs


class ErrorNode(BaseNode):
    error = Inputs.error
