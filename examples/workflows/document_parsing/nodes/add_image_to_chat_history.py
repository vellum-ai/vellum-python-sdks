from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class AddImageToChatHistory(TemplatingNode[BaseState, List[ChatMessage]]):
    """You can use this approach if you want to insert documents into Chat History dynamically while your Workflow / Agent is running."""

    template = """\
{%- set new_msg = {
    \"text\": image_url,
    \"role\": \"USER\",
    \"content\": {
      \"type\": \"ARRAY\",
      \"value\": [
        {
          \"type\": \"DOCUMENT\",
          \"value\": {
            \"src\": image_url,
          }
        }
      ]
    },
    \"source\": None
  } -%}
{%- set msg_arr = [new_msg] -%}
{{- ((chat_history or []) + msg_arr) | tojson -}}\
"""
    inputs = {
        "chat_history": [],
        "image_url": Inputs.image_url,
    }
