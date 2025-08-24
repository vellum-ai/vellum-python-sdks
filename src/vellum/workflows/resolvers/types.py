from typing import NamedTuple, Optional

from vellum.workflows.state.base import BaseState


class LoadStateResult(NamedTuple):
    state: Optional[BaseState]
    previous_trace_id: Optional[str]
    previous_span_id: Optional[str]
    root_trace_id: Optional[str]
    root_span_id: Optional[str]
