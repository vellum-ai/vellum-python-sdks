from typing import List, Optional

from vellum import VellumImage
from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    """Inputs for the internal file upload workflow examples."""

    # Can accept either a public URL or a vellum:uploaded-file:* URI
    image: Optional[VellumImage] = None

    # Can accept multiple images
    images: Optional[List[VellumImage]] = None

    # For examples that need a file path or URL
    file_url: Optional[str] = None
