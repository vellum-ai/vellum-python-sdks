# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime
from ..core.pydantic_utilities import deep_union_pydantic_dicts, pydantic_v1


class OpenApiArrayPropertyRequest(pydantic_v1.BaseModel):
    """
    An OpenAPI specification of a property with type 'array'
    """

    min_items: typing.Optional[int] = None
    max_items: typing.Optional[int] = None
    unique_items: typing.Optional[bool] = None
    items: OpenApiPropertyRequest
    prefix_items: typing.Optional[typing.List[OpenApiPropertyRequest]] = None
    contains: typing.Optional[OpenApiPropertyRequest] = None
    min_contains: typing.Optional[int] = None
    max_contains: typing.Optional[int] = None
    default: typing.Optional[typing.List[typing.Any]] = None
    title: typing.Optional[str] = None
    description: typing.Optional[str] = None

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults_exclude_unset: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        kwargs_with_defaults_exclude_none: typing.Any = {"by_alias": True, "exclude_none": True, **kwargs}

        return deep_union_pydantic_dicts(
            super().dict(**kwargs_with_defaults_exclude_unset), super().dict(**kwargs_with_defaults_exclude_none)
        )

    class Config:
        frozen = True
        smart_union = True
        extra = pydantic_v1.Extra.allow
        json_encoders = {dt.datetime: serialize_datetime}


from .open_api_property_request import OpenApiPropertyRequest  # noqa: E402

OpenApiArrayPropertyRequest.update_forward_refs()
