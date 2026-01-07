from vellum.workflows import BaseWorkflow

from .nodes.my_subworkflow import MySubworkflowNode


class MyNodeWorkflow(BaseWorkflow):
    graph = MySubworkflowNode

    class Outputs(BaseWorkflow.Outputs):
        result = MySubworkflowNode.Outputs.result
