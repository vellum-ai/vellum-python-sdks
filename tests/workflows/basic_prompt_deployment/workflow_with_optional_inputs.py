from typing import Optional

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import PromptDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class InputsWithOptional(BaseInputs):
    city: str
    date: str
    optional_field: Optional[str] = None


class ExamplePromptDeploymentNodeWithOptional(PromptDeploymentNode):
    deployment = "example_prompt_deployment_with_optional"
    prompt_inputs = {
        "city": InputsWithOptional.city,
        "date": InputsWithOptional.date,
        "optional_field": InputsWithOptional.optional_field,
    }


class WorkflowWithOptionalInputs(BaseWorkflow[InputsWithOptional, BaseState]):
    graph = ExamplePromptDeploymentNodeWithOptional

    class Outputs(BaseOutputs):
        results = ExamplePromptDeploymentNodeWithOptional.Outputs.results
        text = ExamplePromptDeploymentNodeWithOptional.Outputs.text
