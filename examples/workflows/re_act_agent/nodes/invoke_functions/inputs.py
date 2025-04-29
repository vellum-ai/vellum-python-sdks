from typing import Any, Optional, Union

from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    index: Optional[Union[float, int]]
    items: Optional[Any]
    item: Optional[Any]
