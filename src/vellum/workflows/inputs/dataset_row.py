from datetime import datetime
import warnings
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from pydantic import ConfigDict, Field, SerializationInfo, field_serializer, model_serializer, model_validator

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.utils.files.mixin import VellumFileMixin
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
        workflow_trigger: Optional Trigger instance for this scenario
        mocks: Optional sequence of node output mocks for testing scenarios
    """

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: Optional[str] = None
    label: str
    inputs: Union[BaseInputs, Dict[str, Any]] = Field(default_factory=BaseInputs)
    workflow_trigger: Optional[BaseTrigger] = None
    mocks: Optional[Sequence[Union[BaseOutputs, MockNodeExecution]]] = None
    # DEPRECATED: node_output_mocks - use mocks instead. Remove in v2.0.0
    node_output_mocks: Optional[Sequence[Union[BaseOutputs, MockNodeExecution]]] = Field(
        default=None,
        exclude=True,  # Don't include in serialized output
    )

    @model_validator(mode="after")
    def _handle_deprecated_node_output_mocks(self) -> "DatasetRow":
        """Handle deprecated node_output_mocks field by mapping it to mocks."""
        if self.node_output_mocks is not None:
            warnings.warn(
                "The 'node_output_mocks' parameter is deprecated and will be removed in v2.0.0. "
                "Please use 'mocks' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            # If mocks is not set, use node_output_mocks value
            if self.mocks is None:
                object.__setattr__(self, "mocks", self.node_output_mocks)
        return self

    @model_serializer(mode="wrap")
    def serialize_full_model(self, handler: Callable[[Any], Any], info: SerializationInfo) -> Dict[str, Any]:
        """Serialize the model and add node_id field computed from then_outputs."""
        serialized = handler(self)
        if not isinstance(serialized, dict):
            return serialized

        # Add deprecation error if node_output_mocks was used - remove in v2.0.0
        if self.node_output_mocks is not None:
            add_error = info.context.get("add_error") if info.context else None
            if add_error is not None:
                add_error(
                    Exception(
                        f'Dataset row "{self.label}": "node_output_mocks" is deprecated. '
                        'Please use "mocks" instead. This will be removed in v2.0.0.'
                    )
                )

        if "mocks" in serialized and serialized.get("mocks") is None:
            serialized.pop("mocks")

        if "workflow_trigger" in serialized:
            value = serialized.pop("workflow_trigger")
            if value is not None:
                serialized["workflow_trigger_id"] = value

        # Merge trigger attribute values into inputs if workflow_trigger is present
        if self.workflow_trigger is not None:
            trigger_attrs = self.workflow_trigger.to_trigger_attribute_values()
            for ref, attr_value in trigger_attrs.items():
                # Convert datetime objects to ISO format strings for JSON serialization
                if isinstance(attr_value, datetime):
                    attr_value = attr_value.isoformat()
                serialized["inputs"][ref.name] = attr_value

        if "id" in serialized and serialized.get("id") is None:
            serialized.pop("id")

        return serialized

    @field_serializer("workflow_trigger")
    def serialize_workflow_trigger(self, workflow_trigger: Optional[BaseTrigger]) -> Optional[str]:
        """
        Custom serializer for workflow_trigger that converts it to a string ID.

        Args:
            workflow_trigger: Optional workflow trigger instance

        Returns:
            String representation of the trigger ID, or None if no trigger
        """
        if workflow_trigger is None:
            return None

        return str(workflow_trigger.__class__.__id__)

    @field_serializer("inputs")
    def serialize_inputs(self, inputs: Union[BaseInputs, Dict[str, Any]], info: SerializationInfo) -> Dict[str, Any]:
        """
        Custom serializer for inputs that converts it to a dictionary.

        When add_error is provided in the serialization context, this method will
        validate file-type inputs (VellumFileMixin) by attempting to serialize them,
        and collect errors for fields that fail to serialize while still including
        valid fields.

        Args:
            inputs: Either a BaseInputs instance or dict to serialize
            info: Serialization info containing context

        Returns:
            Dictionary representation of the inputs
        """
        if isinstance(inputs, dict):
            return inputs

        result = {}
        add_error = info.context.get("add_error") if info.context else None

        for input_descriptor, value in inputs:
            if input_descriptor.name.startswith("__"):
                continue

            # For file types, validate by attempting to serialize and catch errors
            if add_error is not None and isinstance(value, VellumFileMixin):
                try:
                    # Trigger validation by serializing the file type
                    value.model_dump(mode="json", by_alias=True, exclude_none=True)
                    result[input_descriptor.name] = value
                except Exception as field_error:
                    error_msg = (
                        f'Dataset row "{self.label}": input "{input_descriptor.name}" '
                        f"failed serialization: {field_error}"
                    )
                    add_error(Exception(error_msg))
            else:
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
