from typing import Any, Dict, Optional, Sequence, Type, Union

from pydantic import Field, field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.mocks import MockNodeExecution
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.triggers import BaseTrigger


class DatasetRow(UniversalBaseModel):
    """
    Universal base model representing a dataset row with a label and inputs.

    Attributes:
        label: String label for the dataset row
        inputs: BaseInputs instance or dict containing the input data
        workflow_trigger_id: Optional Trigger identifying the workflow trigger class for this scenario
        node_output_mocks: Optional sequence of node output mocks for testing scenarios
    """

    label: str
    inputs: Union[BaseInputs, Dict[str, Any]] = Field(default_factory=BaseInputs)
    workflow_trigger: Optional[Type[BaseTrigger]] = None
    node_output_mocks: Optional[Sequence[Union[BaseOutputs, MockNodeExecution]]] = None

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
