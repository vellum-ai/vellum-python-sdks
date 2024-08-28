# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .ml_model_feature import MlModelFeature
import pydantic
from .ml_model_tokenizer_config_request import MlModelTokenizerConfigRequest
from .ml_model_request_config_request import MlModelRequestConfigRequest
from .ml_model_response_config_request import MlModelResponseConfigRequest
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class MlModelExecConfigRequest(UniversalBaseModel):
    model_identifier: str
    base_url: str
    metadata: typing.Dict[str, typing.Optional[typing.Any]]
    features: typing.List[MlModelFeature]
    force_system_credentials: typing.Optional[bool] = pydantic.Field(default=None)
    """
    For internal use only.
    """

    tokenizer_config: typing.Optional[MlModelTokenizerConfigRequest] = None
    request_config: typing.Optional[MlModelRequestConfigRequest] = None
    response_config: typing.Optional[MlModelResponseConfigRequest] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
