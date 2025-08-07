from typing import Optional

from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    query: str
    context: Optional[str] = None
