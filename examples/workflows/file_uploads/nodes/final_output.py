from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .use_uploaded_file_node import UseUploadedFileNode


class FinalOutput(FinalOutputNode[BaseState, str]):
    """Final output that returns the analysis result."""

    class Outputs(FinalOutputNode.Outputs):
        analysis = UseUploadedFileNode.Outputs.text
