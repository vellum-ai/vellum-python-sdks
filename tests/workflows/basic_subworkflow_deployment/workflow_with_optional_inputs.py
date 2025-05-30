from typing import Optional

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class InputsWithOptional(BaseInputs):
    city: str
    date: str
    optional_field: Optional[str] = None


class ExampleSubworkflowDeploymentNodeWithOptional(SubworkflowDeploymentNode):
    deployment = "example_subworkflow_deployment_with_optional"
    subworkflow_inputs = {
        "city": InputsWithOptional.city,
        "date": InputsWithOptional.date,
        "optional_field": InputsWithOptional.optional_field,
    }

    class Outputs(BaseOutputs):
        temperature: float
        reasoning: str


class WorkflowWithOptionalInputsSubworkflow(BaseWorkflow[InputsWithOptional, BaseState]):
    graph = ExampleSubworkflowDeploymentNodeWithOptional

    class Outputs(BaseOutputs):
        temperature = ExampleSubworkflowDeploymentNodeWithOptional.Outputs.temperature
        reasoning = ExampleSubworkflowDeploymentNodeWithOptional.Outputs.reasoning
