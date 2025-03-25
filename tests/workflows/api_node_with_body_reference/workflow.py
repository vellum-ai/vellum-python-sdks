from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import APIRequestMethod
from vellum.workflows.nodes import APINode
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json


class MyBody(TemplatingNode[BaseState, Json]):
    template = """
{
    "key": "value"
}
"""


class SimpleAPINode(APINode):
    method = APIRequestMethod.POST
    url = "https://testing.vellum.ai/api"
    json = MyBody.Outputs.result


class APINodeWithBodyReferenceWorkflow(BaseWorkflow):
    graph = MyBody >> SimpleAPINode

    class Outputs(BaseWorkflow.Outputs):
        json = SimpleAPINode.Outputs.json
