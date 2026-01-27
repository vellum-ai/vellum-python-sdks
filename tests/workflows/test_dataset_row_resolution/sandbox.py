from typing import List, Union

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow

from .workflow import Inputs

# Dataset with multiple rows for testing resolution by int, string label, and UUID id
dataset: List[Union[BaseInputs, DatasetRow]] = [
    DatasetRow(id="uuid-row-1", label="First Row", inputs=Inputs(message="Hello")),
    DatasetRow(id="uuid-row-2", label="Second Row", inputs=Inputs(message="World")),
    DatasetRow(id="12345678-1234-5678-1234-567812345678", label="UUID Row", inputs=Inputs(message="UUID Test")),
    Inputs(message="BaseInputs Row"),  # This will get default label "Scenario 4"
]
