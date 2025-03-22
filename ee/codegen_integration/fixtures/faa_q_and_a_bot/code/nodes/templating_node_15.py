from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .prompt_node_16 import PromptNode16


class TemplatingNode15(TemplatingNode[BaseState, str]):
    template = """https://aviation-edge.com/v2/public/flights?key={{ API_KEY }}&arrIATA={{ arrival_airport }}&airlineIATA={{ airline_name }}"""
    inputs = {
        "API_KEY": "ab2f59-1004d1",
        "airline_name": "WN",
        "arrival_airport": PromptNode16.Outputs.text,
    }
