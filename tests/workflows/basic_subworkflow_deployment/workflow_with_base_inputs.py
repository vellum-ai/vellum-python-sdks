from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class TestInputs(BaseInputs):
    city: str
    date: str


class ExampleSubworkflowDeploymentNodeWithBaseInputs(SubworkflowDeploymentNode):
    deployment = "example_workflow_deployment"

    subworkflow_inputs = TestInputs(city="San Francisco", date="2024-01-01")

    class Outputs(BaseOutputs):
        temperature: float
        reasoning: str


class WorkflowWithBaseInputsSubworkflow(BaseWorkflow[TestInputs, BaseState]):
    graph = ExampleSubworkflowDeploymentNodeWithBaseInputs

    class Outputs(BaseOutputs):
        temperature = ExampleSubworkflowDeploymentNodeWithBaseInputs.Outputs.temperature
        reasoning = ExampleSubworkflowDeploymentNodeWithBaseInputs.Outputs.reasoning
