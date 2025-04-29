from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState


class AddEvaluatorMessageToChatHistory(TemplatingNode[BaseState, List[ChatMessage]]):
    template = """\
{%- set new_msg = {
  \"role\": \"USER\",
  \"text\": message
} -%}
{%- set msg_arr = [new_msg] -%}
{{- (chat_history + msg_arr) | tojson -}}\
"""
    inputs = {
        "chat_history": LazyReference("AddAgentMessageToChatHistory.Outputs.result"),
        "message": LazyReference("EvaluatorAgent.Outputs.text"),
    }
