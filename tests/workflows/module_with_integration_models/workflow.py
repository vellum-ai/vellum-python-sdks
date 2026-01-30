from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.test_node import TestNode


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = TestNode

    class Outputs(BaseWorkflow.Outputs):
        result = TestNode.Outputs.result
