from typing import Any, Literal, Union

from vellum.client.core.pydantic_utilities import UniversalBaseModel


class BaseStateDelta(UniversalBaseModel):
    name: str


class SetStateDelta(BaseStateDelta):
    delta: Any
    delta_type: Literal["SET_STATE"] = "SET_STATE"


class AppendStateDelta(BaseStateDelta):
    delta: Any
    delta_type: Literal["APPEND_STATE"] = "APPEND_STATE"


StateDelta = Union[SetStateDelta, AppendStateDelta]
