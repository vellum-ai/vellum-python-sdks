from vellum import SystemMessage, UserMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable import InlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    user_query: str


class AutocastingPromptNode(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        SystemMessage("What color is the item?"),
        UserMessage("Here is the user query: {{user_query}}"),
    ]
    prompt_inputs = {
        "user_query": WorkflowInputs.user_query,
    }


class AutocastingPromptWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = AutocastingPromptNode

    class Outputs(BaseOutputs):
        results = AutocastingPromptNode.Outputs.results
