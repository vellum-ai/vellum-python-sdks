from typing import Any, Union

from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    items: Any
    item: Any
    index: Union[float, int]
