from vellum.workflows import BaseWorkflow

from .nodes.node import MySubworkflowNode


class Workflow(BaseWorkflow):
    graph = MySubworkflowNode

    class Outputs(BaseWorkflow.Outputs):
        result = MySubworkflowNode.Outputs.result
