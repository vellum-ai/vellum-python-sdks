from typing import List

from vellum.workflows.inputs.base import BaseInputs


class Inputs(BaseInputs):
    items: List[str]
