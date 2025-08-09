from typing import Optional

from pydantic import Field

from vellum.client.core.pydantic_utilities import UniversalBaseModel


class NodeDisplayPosition(UniversalBaseModel):
    x: float = 0.0
    y: float = 0.0


class NodeDisplayComment(UniversalBaseModel):
    value: Optional[str] = None
    expanded: Optional[bool] = None


class NodeDisplayData(UniversalBaseModel):
    position: NodeDisplayPosition = Field(default_factory=NodeDisplayPosition)
    width: Optional[int] = None
    height: Optional[int] = None
    comment: Optional[NodeDisplayComment] = None
