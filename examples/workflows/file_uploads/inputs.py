from typing import List, Optional

from vellum import VellumImage
from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    """Inputs for the file upload workflow example."""

    images: Optional[List[VellumImage]] = None
