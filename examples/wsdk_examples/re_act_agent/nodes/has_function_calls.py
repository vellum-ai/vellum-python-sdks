from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .agent_node import AgentNode


class HasFunctionCalls(TemplatingNode[BaseState, str]):
    template = """{{- output | selectattr(\'type\', \'equalto\', \'FUNCTION_CALL\') | list | length > 0 -}}"""
    inputs = {
        "output": AgentNode.Outputs.results,
    }
