from uuid import UUID
from typing import Dict

from vellum.workflows.utils.uuids import uuid4_from_hash


class BaseExecutable:
    __id__: UUID = uuid4_from_hash(__qualname__)
    __output_ids__: Dict[str, UUID] = {}
