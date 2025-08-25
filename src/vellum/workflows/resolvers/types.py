from typing import NamedTuple

from vellum.workflows.state.base import BaseState


class LoadStateResult(NamedTuple):
    state: BaseState
    previous_trace_id: str
    previous_span_id: str
    root_trace_id: str
    root_span_id: str
