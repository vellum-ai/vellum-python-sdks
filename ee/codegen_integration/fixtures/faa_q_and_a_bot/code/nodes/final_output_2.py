from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState

from .prompt_node_14 import PromptNode14
from .prompt_node_19 import PromptNode19


class FinalOutput2(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = (
            LazyReference("PromptNode9.Outputs.text")
            .coalesce(PromptNode14.Outputs.text)
            .coalesce(LazyReference("PromptNode18.Outputs.text"))
            .coalesce(PromptNode19.Outputs.text)
        )
