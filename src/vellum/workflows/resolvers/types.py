from typing import NamedTuple, Optional

from vellum.workflows.state.base import BaseState


class SpanLinkInfo(NamedTuple):
    previous_trace_id: str
    previous_span_id: str
    root_trace_id: str
    root_span_id: str


class LoadStateResult(NamedTuple):
    state: Optional[BaseState]
    span_link_info: Optional[SpanLinkInfo]
