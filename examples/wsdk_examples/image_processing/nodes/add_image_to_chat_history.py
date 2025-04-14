from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class AddImageToChatHistory(TemplatingNode[BaseState, List[ChatMessage]]):
    """You can use this approach if you want to insert images into Chat History dynamically while your Workflow / Agent is running. You may want this if you want to process images at runtime, for example, images included in a parsed document or webpage."""

    template = """\
{%- set new_msg = {
    \"text\": image_url,
    \"role\": \"USER\",
    \"content\": {
      \"type\": \"ARRAY\",
      \"value\": [
        {
          \"type\": \"IMAGE\",
          \"value\": {
            \"src\": image_url,
            \"metadata\": {
              \"detail\": \"low\"
            }
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
