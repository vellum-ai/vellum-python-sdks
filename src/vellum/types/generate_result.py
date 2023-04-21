# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

import pydantic

from ..core.datetime_utils import serialize_datetime
from .generate_result_data import GenerateResultData
from .generate_result_error import GenerateResultError


class GenerateResult(pydantic.BaseModel):
    data: typing.Optional[GenerateResultData] = pydantic.Field(
        description=(
            "An object containing the resulting generation. This key will be absent if the LLM provider experienced an error.\n"
        )
    )
    error: typing.Optional[GenerateResultError] = pydantic.Field(
        description=(
            "An object containing details about the error that occurred. This key will be absent if the LLM provider did not experience an error.\n"
        )
    )

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        json_encoders = {dt.datetime: serialize_datetime}
