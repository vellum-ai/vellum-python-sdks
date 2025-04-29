from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .evaluator_agent import EvaluatorAgent


class ExtractStatus(TemplatingNode[BaseState, str]):
    template = """{{ json.loads(example_var_1)[\"status\"] }}"""
    inputs = {
        "example_var_1": EvaluatorAgent.Outputs.text,
    }
