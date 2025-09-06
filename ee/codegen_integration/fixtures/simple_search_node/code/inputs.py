from typing import Optional

from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    query: Optional[str] = "Search node query default"
    var1: str
