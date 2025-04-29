from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json


class AllowedFunctionNames(TemplatingNode[BaseState, Json]):
    template = """[\"get_current_weather\"]"""
    inputs = {}
