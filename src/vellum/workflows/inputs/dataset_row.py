from typing import Any, Dict, Union

from pydantic import Field, field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.inputs.base import BaseInputs


class DatasetRow(UniversalBaseModel):
    """
    Universal base model representing a dataset row with a label and inputs.

    Attributes:
        label: String label for the dataset row
        inputs: BaseInputs instance or dict containing the input data
    """

    label: str
    inputs: Union[BaseInputs, Dict[str, Any]] = Field(default_factory=BaseInputs)

    @field_serializer("inputs")
    def serialize_inputs(self, inputs: Union[BaseInputs, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Custom serializer for inputs that converts it to a dictionary.

        Args:
            inputs: Either a BaseInputs instance or dict to serialize

        Returns:
            Dictionary representation of the inputs
        """
        if isinstance(inputs, dict):
            return inputs

        result = {}
        for input_descriptor, value in inputs:
            if not input_descriptor.name.startswith("__"):
                result[input_descriptor.name] = value

        return result
