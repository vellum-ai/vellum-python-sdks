from vellum.workflows.nodes.bases import BaseNode


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result = "Hello from SimpleNode"
