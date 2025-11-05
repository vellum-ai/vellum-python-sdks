from abc import ABC
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Set, Tuple, Type

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode, BaseNodeMeta
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.core import MergeBehavior
from vellum.workflows.types.generics import StateType

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow


class _BaseAdornmentNodeMeta(BaseNodeMeta):
    def __new__(cls, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        node_class = super().__new__(cls, name, bases, dct)

        SubworkflowInputs = dct.get("SubworkflowInputs")
        if (
            isinstance(SubworkflowInputs, type)
            and issubclass(SubworkflowInputs, BaseInputs)
            and SubworkflowInputs.__parent_class__ is type(None)
        ):
            SubworkflowInputs.__parent_class__ = node_class

        subworkflow_attribute = dct.get("subworkflow")
        if not subworkflow_attribute:
            return node_class

        if not issubclass(node_class, BaseAdornmentNode):
            raise ValueError("BaseAdornableNodeMeta can only be used on subclasses of BaseAdornableNode")

        subworkflow_outputs = getattr(subworkflow_attribute, "Outputs")
        if not issubclass(subworkflow_outputs, BaseOutputs):
            raise ValueError("subworkflow.Outputs must be a subclass of BaseOutputs")

        outputs_class = dct.get("Outputs")
        if not outputs_class:
            raise ValueError("Outputs class not found in base classes")

        if not issubclass(outputs_class, BaseNode.Outputs):
            raise ValueError("Outputs class must be a subclass of BaseNode.Outputs")

        for descriptor in subworkflow_outputs:
            node_class.__annotate_outputs_class__(outputs_class, descriptor)

        return node_class

    def __getattribute__(cls, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name != "__wrapped_node__" and issubclass(cls, BaseAdornmentNode):
                return getattr(cls.__wrapped_node__, name)
            raise

    @property
    def _localns(cls) -> Dict[str, Any]:
        if not hasattr(cls, "SubworkflowInputs"):
            return super()._localns

        return {
            **super()._localns,
            "SubworkflowInputs": getattr(cls, "SubworkflowInputs"),
        }


class BaseAdornmentNode(
    BaseNode[StateType],
    Generic[StateType],
    ABC,
    metaclass=_BaseAdornmentNodeMeta,
):
    """
    A base node that enables the node to be used as an adornment - meaning it can wrap another node. The
    wrapped node is stored in the `__wrapped_node__` attribute and is redefined as a single-node subworkflow.
    """

    __wrapped_node__: Optional[Type["BaseNode"]] = None
    subworkflow: Type["BaseWorkflow"]

    class Trigger(BaseNode.Trigger):
        """
        Trigger class for adornment nodes that delegates to the wrapped node's Trigger
        for proper merge behavior handling.
        """

        @classmethod
        def should_initiate(
            cls,
            state: StateType,
            dependencies: Set["Type[BaseNode]"],
            node_span_id: UUID,
        ) -> bool:
            """
            Delegates to the wrapped node's Trigger.should_initiate method to ensure
            proper merge behavior (like AWAIT_ALL) is respected for initiation logic.
            """
            # Get the wrapped node's Trigger class
            wrapped_node = cls.node_class.__wrapped_node__
            if wrapped_node is not None:
                wrapped_trigger = wrapped_node.Trigger
                # Only delegate if the wrapped node has a specific merge behavior
                # that differs from the default AWAIT_ATTRIBUTES
                if (
                    hasattr(wrapped_trigger, "merge_behavior")
                    and wrapped_trigger.merge_behavior != MergeBehavior.AWAIT_ATTRIBUTES
                ):
                    return wrapped_trigger.should_initiate(state, dependencies, node_span_id)

            # Fallback to the base implementation if no wrapped node
            return super().should_initiate(state, dependencies, node_span_id)

        @classmethod
        def _queue_node_execution(
            cls, state: StateType, dependencies: set[Type[BaseNode]], invoked_by: Optional[UUID] = None
        ) -> UUID:
            """
            Delegates to the wrapped node's Trigger._queue_node_execution method to ensure
            proper merge behavior (like AWAIT_ALL) is respected for dependency tracking.
            """
            # Get the wrapped node's Trigger class
            wrapped_node = cls.node_class.__wrapped_node__
            if wrapped_node is not None:
                wrapped_trigger = wrapped_node.Trigger
                # Delegate to the wrapped node's trigger logic for queuing
                return wrapped_trigger._queue_node_execution(state, dependencies, invoked_by)

            # Fallback to the base implementation if no wrapped node
            return super()._queue_node_execution(state, dependencies, invoked_by)

    @classmethod
    def __annotate_outputs_class__(cls, outputs_class: Type[BaseOutputs], reference: OutputReference) -> None:
        # Subclasses of BaseAdornableNode can override this method to provider their own
        # approach to annotating the outputs class based on the `subworkflow.Outputs`
        setattr(outputs_class, reference.name, reference)
        if cls.__wrapped_node__:
            cls.__output_ids__[reference.name] = cls.__wrapped_node__.__output_ids__[reference.name]
