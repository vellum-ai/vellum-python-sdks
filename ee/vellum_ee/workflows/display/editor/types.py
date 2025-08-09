from typing import Optional

from pydantic import Field, field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel


class NodeDisplayPosition(UniversalBaseModel):
    x: float = 0.0
    y: float = 0.0


class NodeDisplayComment(UniversalBaseModel):
    value: Optional[str] = None
    expanded: Optional[bool] = None

    @field_serializer("expanded")
    def serialize_expanded(self, expanded: Optional[bool]) -> Optional[bool]:
        if self.value and expanded is None:
            return True
        return expanded


class NodeDisplayData(UniversalBaseModel):
    position: NodeDisplayPosition = Field(default_factory=NodeDisplayPosition)
    width: Optional[int] = None
    height: Optional[int] = None
    comment: Optional[NodeDisplayComment] = None
