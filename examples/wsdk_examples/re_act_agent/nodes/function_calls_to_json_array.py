from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json

from .agent_node import AgentNode


class FunctionCallsToJSONArray(TemplatingNode[BaseState, Json]):
    template = """{{- prompt_outputs | selectattr(\'type\', \'equalto\', \'FUNCTION_CALL\') | list | replace(\"\\n\",\",\") -}}"""
    inputs = {
        "prompt_outputs": AgentNode.Outputs.results,
    }
