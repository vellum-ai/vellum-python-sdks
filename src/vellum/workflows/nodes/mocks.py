import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Sequence, Type, Union

from pydantic import (
    ConfigDict,
    SerializationInfo,
    ValidationError,
    ValidationInfo,
    field_serializer,
    field_validator,
    model_serializer,
)

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.array_vellum_value import ArrayVellumValue
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.types import default_serializer
from vellum.workflows.exceptions import NodeException, WorkflowInitializationException
from vellum.workflows.nodes.utils import get_unadorned_node
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.constant import ConstantValueReference

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow

logger = logging.getLogger(__name__)


class MockNodeExecution(UniversalBaseModel):
    when_condition: BaseDescriptor
    then_outputs: BaseOutputs
    disabled: Optional[bool] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("when_condition", mode="before")
    @classmethod
    def normalize_when_condition(cls, v: Any, info: ValidationInfo) -> BaseDescriptor:
        """Normalize when_condition to a BaseDescriptor.

        - If already a BaseDescriptor, return unchanged
        - If a dict with 'type' key (serialized descriptor), use descriptor_validator from context
        - Otherwise, wrap as ConstantValueReference (for constants like True, False, strings, etc.)
        """
        if isinstance(v, BaseDescriptor):
            return v

        if isinstance(v, dict) and "type" in v:
            ctx = info.context or {}
            descriptor_validator = ctx.get("descriptor_validator")
            if callable(descriptor_validator):
                return descriptor_validator(v)

        return ConstantValueReference(v)

    @model_serializer(mode="wrap")
    def serialize_full_model(self, handler: Callable[[Any], Any], info: SerializationInfo) -> Dict[str, Any]:
        """Serialize the model and add node_id field computed from then_outputs."""
        serialized = handler(self)
        node_class = self.then_outputs.__class__.__parent_class__
        unadorned_node = get_unadorned_node(node_class)  # type: ignore[arg-type]
        serialized["node_id"] = str(unadorned_node.__id__)
        serialized["type"] = "NODE_EXECUTION"
        if self.disabled is None:
            del serialized["disabled"]
        return serialized

    @field_serializer("then_outputs")
    def serialize_then_outputs(self, then_outputs: BaseOutputs, _info: SerializationInfo) -> Dict[str, Any]:
        return default_serializer(then_outputs)

    @field_serializer("when_condition")
    def serialize_when_condition(self, when_condition: BaseDescriptor, info: SerializationInfo) -> Dict[str, Any]:
        # This allows `ee` to pass in workflow display context through the pydantic context
        if isinstance(info.context, dict) and "serializer" in info.context and callable(info.context["serializer"]):
            return info.context["serializer"](when_condition)

        return default_serializer(when_condition)

    @staticmethod
    def validate_all(
        raw_mock_workflow_node_configs: Optional[List[Any]],
        workflow: Type["BaseWorkflow"],
        descriptor_validator: Optional[Callable[[dict, Type["BaseWorkflow"]], BaseDescriptor]] = None,
    ) -> Optional[List["MockNodeExecution"]]:
        if not raw_mock_workflow_node_configs:
            return None

        ArrayVellumValue.model_rebuild()
        mock_node_executions: list[MockNodeExecution] = []
        for raw_mock_workflow_node_config in raw_mock_workflow_node_configs:
            if not isinstance(raw_mock_workflow_node_config, dict):
                raise WorkflowInitializationException(
                    message=f"Invalid mock node execution type: {type(raw_mock_workflow_node_config)}",
                    code=WorkflowErrorCode.INVALID_INPUTS,
                    workflow_definition=workflow,
                )

            try:
                mock_node_executions.append(
                    MockNodeExecution.model_validate(
                        raw_mock_workflow_node_config,
                        context={
                            "workflow": workflow,
                            "node_id": raw_mock_workflow_node_config.get("node_id"),
                            "descriptor_validator": (
                                (lambda value: descriptor_validator(value, workflow)) if descriptor_validator else None
                            ),
                        },
                    )
                )
            except WorkflowInitializationException as e:
                # If the node is not found in the workflow, skip it with a warning
                node_id = raw_mock_workflow_node_config.get("node_id")
                # Handle case where raw_data could be a string (not a dict)
                raw_data = e.raw_data if isinstance(e.raw_data, dict) else {}
                if raw_data.get("node_ref") == node_id:
                    logger.warning(
                        "Skipping mock for node %s: node not found in workflow %s",
                        node_id,
                        workflow.__name__,
                    )
                    continue
                raise
            except (ValidationError, NodeException) as e:
                raise WorkflowInitializationException(
                    message="Failed to validate mock node executions",
                    code=WorkflowErrorCode.INVALID_INPUTS,
                    workflow_definition=workflow,
                ) from e

        return mock_node_executions


MockNodeExecutionArg = Sequence[Union[BaseOutputs, MockNodeExecution]]
