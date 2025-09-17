from typing import Any, Dict, Optional

from pydantic import field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.inputs.base import BaseInputs


class DatasetRow(UniversalBaseModel):
    """
    Universal base model representing a dataset row with a label and inputs.

    Attributes:
        label: String label for the dataset row
        inputs: BaseInputs instance containing the input data (optional)
    """

    label: str
    inputs: Optional[BaseInputs] = None

    @field_serializer("inputs")
    def serialize_inputs(self, inputs: Optional[BaseInputs]) -> Dict[str, Any]:
        """
        Custom serializer for BaseInputs that converts it to a dictionary.

        Args:
            inputs: BaseInputs instance to serialize (can be None)

        Returns:
            Dictionary representation of the inputs, or empty dict if None
        """
        if inputs is None:
            return {}

        result = {}

        for input_descriptor, value in inputs:
            if not input_descriptor.name.startswith("__"):
                result[input_descriptor.name] = value

        return result
