from typing import Any, Dict, Optional

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
    z_index: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    comment: Optional[NodeDisplayComment] = None

    def dict_exclude_none_display_fields(self) -> Dict[str, Any]:
        """
        Serialize to dict, excluding z_index, width, and height when they are None.
        """
        result = self.dict()

        if result.get("z_index") is None:
            result.pop("z_index", None)
        if result.get("width") is None:
            result.pop("width", None)
        if result.get("height") is None:
            result.pop("height", None)

        return result
