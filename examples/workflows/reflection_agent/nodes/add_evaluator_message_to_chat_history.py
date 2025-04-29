from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .add_agent_message_to_chat_history import AddAgentMessageToChatHistory
from .evaluator_agent import EvaluatorAgent


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
        "chat_history": AddAgentMessageToChatHistory.Outputs.result,
        "message": EvaluatorAgent.Outputs.text,
    }
