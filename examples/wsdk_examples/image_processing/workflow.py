from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.add_image_to_chat_history import AddImageToChatHistory
from .nodes.final_output import FinalOutput
from .nodes.final_output_6 import FinalOutput6
from .nodes.summarize_image_by_chat_history import SummarizeImageByChatHistory
from .nodes.summarize_image_by_url_chat_history import SummarizeImageByURLChatHistory


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        SummarizeImageByChatHistory >> FinalOutput6,
        AddImageToChatHistory >> SummarizeImageByURLChatHistory >> FinalOutput,
    }

    class Outputs(BaseWorkflow.Outputs):
        final_output_6 = FinalOutput6.Outputs.value
        final_output = FinalOutput.Outputs.value
