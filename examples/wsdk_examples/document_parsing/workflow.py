from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.add_image_to_chat_history import AddImageToChatHistory
from .nodes.extract_by_chat_history import ExtractByChatHistory
from .nodes.extract_by_document_url import ExtractByDocumentURL
from .nodes.final_output import FinalOutput
from .nodes.final_output_6 import FinalOutput6


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        ExtractByChatHistory >> FinalOutput6,
        AddImageToChatHistory >> ExtractByDocumentURL >> FinalOutput,
    }

    class Outputs(BaseWorkflow.Outputs):
        final_output_6 = FinalOutput6.Outputs.value
        final_output = FinalOutput.Outputs.value
