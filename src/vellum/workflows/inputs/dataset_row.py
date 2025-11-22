from typing import Any, Dict, List, Optional, Sequence, Type, Union

from pydantic import Field, field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.mocks import MockNodeExecution
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.triggers import BaseTrigger


class DatasetRow(UniversalBaseModel):
    """
    Universal base model representing a dataset row with a label and inputs.

    Attributes:
        id: Optional unique identifier for the dataset row
        label: String label for the dataset row
        inputs: BaseInputs instance or dict containing the input data
        workflow_trigger_id: Optional Trigger identifying the workflow trigger class for this scenario
        node_output_mocks: Optional sequence of node output mocks for testing scenarios
    """

    id: Optional[str] = None
    label: str
    inputs: Union[BaseInputs, Dict[str, Any]] = Field(default_factory=BaseInputs)
    workflow_trigger: Optional[Type[BaseTrigger]] = None
    node_output_mocks: Optional[Sequence[Union[BaseOutputs, MockNodeExecution]]] = None

    @field_serializer("workflow_trigger")
    def serialize_workflow_trigger(self, workflow_trigger: Optional[Type[BaseTrigger]]) -> Optional[str]:
        """
        Custom serializer for workflow_trigger that converts it to a string ID.

        Args:
            workflow_trigger: Optional workflow trigger class

        Returns:
            String representation of the trigger ID, or None if no trigger
        """
        return str(workflow_trigger.__id__) if workflow_trigger is not None else None

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

    @field_serializer("node_output_mocks")
    def serialize_node_output_mocks(
        self, node_output_mocks: Optional[Sequence[Union[BaseOutputs, MockNodeExecution]]], info
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Custom serializer for node_output_mocks that normalizes both BaseOutputs and MockNodeExecution
        to a consistent dict format with node_id, when_condition, and then_outputs.

        Args:
            node_output_mocks: Optional sequence of BaseOutputs or MockNodeExecution instances
            info: Serialization info containing context

        Returns:
            List of normalized mock execution dicts, or None if input is None
        """
        if node_output_mocks is None:
            return None

        result = []
        for mock in node_output_mocks:
            if isinstance(mock, MockNodeExecution):
                mock_exec = mock
            else:
                mock_exec = MockNodeExecution(
                    when_condition=ConstantValueReference(True),
                    then_outputs=mock,
                )

            result.append(mock_exec.model_dump(context=info.context))

        return result
