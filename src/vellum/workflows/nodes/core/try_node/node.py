import sys
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Iterator, Optional, Set, Tuple, Type, TypeVar

from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base import BaseNodeMeta
from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.generics import StateType
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow

Subworkflow = Type["BaseWorkflow"]
_T = TypeVar("_T", bound=BaseOutputs)


class _TryNodeMeta(BaseNodeMeta):
    def __new__(cls, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        node_class = super().__new__(cls, name, bases, dct)

        subworkflow_attribute = dct.get("subworkflow")
        if not subworkflow_attribute:
            return node_class

        subworkflow_outputs = getattr(subworkflow_attribute, "Outputs")
        if not issubclass(subworkflow_outputs, BaseOutputs):
            raise ValueError("subworkflow.Outputs must be a subclass of BaseOutputs")

        outputs_class = dct.get("Outputs")
        if not outputs_class:
            raise ValueError("Outputs class not found in base classes")

        if not issubclass(outputs_class, BaseNode.Outputs):
            raise ValueError("Outputs class must be a subclass of BaseNode.Outputs")

        for descriptor in subworkflow_outputs:
            if descriptor.name == "error":
                raise ValueError("`error` is a reserved name for TryNode.Outputs")

            setattr(outputs_class, descriptor.name, descriptor)

        return node_class

    def __getattribute__(cls, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name != "__wrapped_node__" and issubclass(cls, TryNode):
                return getattr(cls.__wrapped_node__, name)
            raise


class TryNode(BaseNode[StateType], Generic[StateType], metaclass=_TryNodeMeta):
    """
    Used to execute a Subworkflow and handle errors.

    on_error_code: Optional[VellumErrorCode] = None - The error code to handle
    subworkflow: Type["BaseWorkflow"] - The Subworkflow to execute
    """

    __wrapped_node__: Optional[Type["BaseNode"]] = None
    on_error_code: Optional[WorkflowErrorCode] = None
    subworkflow: Type["BaseWorkflow"]

    class Outputs(BaseNode.Outputs):
        error: Optional[WorkflowError] = None

    def run(self) -> Iterator[BaseOutput]:
        subworkflow = self.subworkflow(
            parent_state=self.state,
            context=WorkflowContext(vellum_client=self._context.vellum_client),
        )
        subworkflow_stream = subworkflow.stream(
            event_filter=all_workflow_event_filter,
        )

        outputs: Optional[BaseOutputs] = None
        exception: Optional[NodeException] = None
        fulfilled_output_names: Set[str] = set()

        for event in subworkflow_stream:
            self._context._emit_subworkflow_event(event)
            if exception:
                continue

            if event.name == "workflow.execution.streaming":
                if event.output.is_fulfilled:
                    fulfilled_output_names.add(event.output.name)
                yield event.output
            elif event.name == "workflow.execution.fulfilled":
                outputs = event.outputs
            elif event.name == "workflow.execution.paused":
                exception = NodeException(
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                    message="Subworkflow unexpectedly paused within Try Node",
                )
            elif event.name == "workflow.execution.rejected":
                if self.on_error_code and self.on_error_code != event.error.code:
                    exception = NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message=f"""Unexpected rejection: {event.error.code.value}.
Message: {event.error.message}""",
                    )
                else:
                    outputs = self.Outputs(error=event.error)

        if exception:
            raise exception

        if outputs is None:
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message="Expected to receive outputs from Try Node's subworkflow",
            )

        # For any outputs somehow in our final fulfilled outputs array,
        # but not fulfilled by the stream.
        for descriptor, value in outputs:
            if descriptor.name not in fulfilled_output_names:
                yield BaseOutput(
                    name=descriptor.name,
                    value=value,
                )

    @classmethod
    def wrap(cls, on_error_code: Optional[WorkflowErrorCode] = None) -> Callable[..., Type["TryNode"]]:
        _on_error_code = on_error_code

        def decorator(inner_cls: Type[BaseNode]) -> Type["TryNode"]:
            # Investigate how to use dependency injection to avoid circular imports
            # https://app.shortcut.com/vellum/story/4116
            from vellum.workflows import BaseWorkflow

            inner_cls._is_wrapped_node = True

            class Subworkflow(BaseWorkflow):
                graph = inner_cls

                # mypy is wrong here, this works and is defined
                class Outputs(inner_cls.Outputs):  # type: ignore[name-defined]
                    pass

            dynamic_module = f"{inner_cls.__module__}.{inner_cls.__name__}.{ADORNMENT_MODULE_NAME}"
            # This dynamic module allows calls to `type_hints` to work
            sys.modules[dynamic_module] = ModuleType(dynamic_module)

            # We use a dynamic wrapped node class to be uniquely tied to this `inner_cls` node during serialization
            WrappedNode = type(
                cls.__name__,
                (TryNode,),
                {
                    "__wrapped_node__": inner_cls,
                    "__module__": dynamic_module,
                    "on_error_code": _on_error_code,
                    "subworkflow": Subworkflow,
                    "Ports": type("Ports", (TryNode.Ports,), {port.name: port.copy() for port in inner_cls.Ports}),
                },
            )
            return WrappedNode

        return decorator
