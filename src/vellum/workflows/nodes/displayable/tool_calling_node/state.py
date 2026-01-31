from typing import Any, Dict, List, Optional, TypedDict

from vellum import ChatMessage
from vellum.workflows.state.base import BaseState


class FunctionCallData(TypedDict):
    """Data for a function call extracted from prompt results."""

    arguments: Dict[str, Any]
    function_call_id: Optional[str]


class ToolCallingState(BaseState):
    chat_history: List[ChatMessage] = []
    prompt_iterations: int = 0
    current_prompt_output_index: int = 0
    current_function_calls_processed: int = 0
    # Mapping of function name to its call data, populated in parallel mode
    function_calls_by_name: Dict[str, FunctionCallData] = {}
