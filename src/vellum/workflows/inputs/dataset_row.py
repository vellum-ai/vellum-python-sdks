from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from pydantic import ConfigDict, Field, SerializationInfo, field_serializer, model_serializer

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
        workflow_trigger: Optional Trigger instance or class for this scenario (can be passed as 'trigger' kwarg)
        mocks: Optional sequence of node output mocks for testing scenarios
    """

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: Optional[str] = None
    label: str
    inputs: Union[BaseInputs, Dict[str, Any]] = Field(default_factory=BaseInputs)
    workflow_trigger: Optional[Union[BaseTrigger, Type[BaseTrigger]]] = Field(default=None, alias="trigger")
    mocks: Optional[Sequence[Union[BaseOutputs, MockNodeExecution]]] = None

    @model_serializer(mode="wrap")
    def serialize_full_model(self, handler: Callable[[Any], Any], info: SerializationInfo) -> Dict[str, Any]:
        """Serialize the model and add node_id field computed from then_outputs."""
        serialized = handler(self)
        if not isinstance(serialized, dict):
            return serialized

        if "mocks" in serialized and serialized.get("mocks") is None:
            serialized.pop("mocks")

        if "workflow_trigger" in serialized:
            if serialized.get("workflow_trigger") is None:
                serialized.pop("workflow_trigger")
            else:
                serialized["workflow_trigger_id"] = serialized.pop("workflow_trigger")

        if "id" in serialized and serialized.get("id") is None:
            serialized.pop("id")

        return serialized

    @field_serializer("workflow_trigger")
    def serialize_workflow_trigger(
        self, workflow_trigger: Optional[Union[BaseTrigger, Type[BaseTrigger]]]
    ) -> Optional[str]:
        """
        Custom serializer for workflow_trigger that converts it to a string ID.

        Args:
            workflow_trigger: Optional workflow trigger instance or class

        Returns:
            String representation of the trigger ID, or None if no trigger
        """
        if workflow_trigger is None:
            return None

        # Handle both instances and classes
        if isinstance(workflow_trigger, type):
            # It's a class
            return str(workflow_trigger.__id__)
        else:
            # It's an instance - get __id__ from the class
            return str(workflow_trigger.__class__.__id__)

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

    @field_serializer("mocks")
    def serialize_mocks(
        self, mocks: Optional[Sequence[Union[BaseOutputs, MockNodeExecution]]], info
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Custom serializer for mocks that normalizes both BaseOutputs and MockNodeExecution
        to a consistent dict format with node_id, when_condition, and then_outputs.

        Args:
            mocks: Optional sequence of BaseOutputs or MockNodeExecution instances
            info: Serialization info containing context

        Returns:
            List of normalized mock execution dicts, or None if input is None
        """
        if mocks is None:
            return None

        result = []
        for mock in mocks:
            if isinstance(mock, MockNodeExecution):
                mock_exec = mock
            else:
                mock_exec = MockNodeExecution(
                    when_condition=ConstantValueReference(True),
                    then_outputs=mock,
                )

            result.append(mock_exec.model_dump(context=info.context))

        return result
