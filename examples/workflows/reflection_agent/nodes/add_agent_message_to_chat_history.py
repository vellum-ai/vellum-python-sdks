from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .problem_solver_agent import ProblemSolverAgent


class AddAgentMessageToChatHistory(TemplatingNode[BaseState, List[ChatMessage]]):
    template = """\
{%- set new_msg = {
  \"role\": \"ASSISTANT\",
  \"text\": message
} -%}
{%- set msg_arr = [new_msg] -%}
{{- (chat_history + msg_arr) | tojson -}}\
"""
    inputs = {
        "chat_history": [],
        "message": ProblemSolverAgent.Outputs.text,
    }
