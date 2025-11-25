from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.final_output import FinalOutput
from .nodes.upload_file_node import UploadFileNode
from .nodes.use_uploaded_file_node import UseUploadedFileNode


class Workflow(BaseWorkflow[Inputs, BaseState]):
    """
    Workflow demonstrating file uploads.

    This workflow shows:
    1. How to upload files to Vellum's internal storage
    2. How to use vellum:uploaded-file:* URIs
    3. How to pass images between nodes
    """

    graph = {
        UploadFileNode >> UseUploadedFileNode >> FinalOutput,
    }

    class Outputs(BaseWorkflow.Outputs):
        analysis = FinalOutput.Outputs.analysis
