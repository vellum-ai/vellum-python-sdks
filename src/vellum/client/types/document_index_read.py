# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import datetime as dt
import pydantic
import typing
from .entity_status import EntityStatus
from .document_index_indexing_config import DocumentIndexIndexingConfig
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class DocumentIndexRead(UniversalBaseModel):
    id: str
    created: dt.datetime
    label: str = pydantic.Field()
    """
    A human-readable label for the document index
    """

    name: str = pydantic.Field()
    """
    A name that uniquely identifies this index within its workspace
    """

    status: typing.Optional[EntityStatus] = pydantic.Field(default=None)
    """
    The current status of the document index
    
    * `ACTIVE` - Active
    * `ARCHIVED` - Archived
    """

    indexing_config: DocumentIndexIndexingConfig

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
