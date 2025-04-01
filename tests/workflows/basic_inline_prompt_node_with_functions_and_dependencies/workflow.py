from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from tests.workflows.basic_inline_prompt_node_with_functions_and_dependencies.inputs import WorkflowInputs
from tests.workflows.basic_inline_prompt_node_with_functions_and_dependencies.node import StartNode
from tests.workflows.basic_inline_prompt_node_with_functions_and_dependencies.prompt_node import (
    ExampleBaseInlinePromptNodeWithFunctions,
)


class BasicInlinePromptWithFunctionsWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = StartNode >> ExampleBaseInlinePromptNodeWithFunctions

    class Outputs(BaseWorkflow.Outputs):
        results = ExampleBaseInlinePromptNodeWithFunctions.Outputs.results
