# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import pydantic
import typing
from .indexing_state_enum import IndexingStateEnum
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class DocumentDocumentToDocumentIndex(UniversalBaseModel):
    """
    A detailed representation of the link between a Document and a Document Index it's a member of.
    """

    id: str = pydantic.Field()
    """
    Vellum-generated ID that uniquely identifies this link.
    """

    document_index_id: str = pydantic.Field()
    """
    Vellum-generated ID that uniquely identifies the index this document is included in.
    """

    indexing_state: typing.Optional[IndexingStateEnum] = pydantic.Field(default=None)
    """
    An enum value representing where this document is along its indexing lifecycle for this index.
    
    - `AWAITING_PROCESSING` - Awaiting Processing
    - `QUEUED` - Queued
    - `INDEXING` - Indexing
    - `INDEXED` - Indexed
    - `FAILED` - Failed
    """

    extracted_text_file_url: typing.Optional[str] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
