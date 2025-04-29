from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json


class FunctionCallsToJSONArray(TemplatingNode[BaseState, Json]):
    template = """{{- prompt_outputs | selectattr(\'type\', \'equalto\', \'FUNCTION_CALL\') | list | replace(\"\\n\",\",\") -}}"""
    inputs = {
        "prompt_outputs": LazyReference("AgentNode.Outputs.results"),
    }
