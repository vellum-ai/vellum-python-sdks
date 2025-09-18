from typing import Any, Dict

from pydantic import Field, field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.inputs.base import BaseInputs


class DatasetRow(UniversalBaseModel):
    """
    Universal base model representing a dataset row with a label and inputs.

    Attributes:
        label: String label for the dataset row
        inputs: BaseInputs instance containing the input data
    """

    label: str
    inputs: BaseInputs = Field(default_factory=BaseInputs)

    @field_serializer("inputs")
    def serialize_inputs(self, inputs: BaseInputs) -> Dict[str, Any]:
        """
        Custom serializer for BaseInputs that converts it to a dictionary.

        Args:
            inputs: BaseInputs instance to serialize

        Returns:
            Dictionary representation of the inputs
        """
        result = {}

        for input_descriptor, value in inputs:
            if not input_descriptor.name.startswith("__"):
                result[input_descriptor.name] = value

        return result
