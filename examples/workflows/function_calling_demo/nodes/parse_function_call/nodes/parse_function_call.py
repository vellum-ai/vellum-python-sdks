from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json


@TryNode.wrap()
class ParseFunctionCall1(TemplatingNode[BaseState, Json]):
    template = """{{ json.dumps(json.loads(output).tool_calls[0]) }}"""
    inputs = {
        "output": LazyReference("PromptNode.Outputs.text"),
    }
