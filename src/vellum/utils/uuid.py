import uuid
from typing import Union


def is_valid_uuid(val: Union[str, uuid.UUID, None]) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError):
        return False
