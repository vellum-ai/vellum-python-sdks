# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
import typing
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class NodeEventDisplayContext(UniversalBaseModel):
    input_display: typing.Dict[str, str]
    output_display: typing.Dict[str, str]
    port_display: typing.Dict[str, str]
    subworkflow_display: typing.Optional["WorkflowEventDisplayContext"] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


from .workflow_event_display_context import WorkflowEventDisplayContext  # noqa: E402

update_forward_refs(WorkflowEventDisplayContext, NodeEventDisplayContext=NodeEventDisplayContext)
update_forward_refs(NodeEventDisplayContext)
