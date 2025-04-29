from typing import Any, Optional, Union

from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    index: Optional[Union[float, int]] = None
    items: Optional[Any] = None
    item: Optional[Any] = None
