from typing import TYPE_CHECKING, Any, Dict, Generic, List, Literal, Optional, Set, Type, Union

from pydantic import SerializerFunctionWrapHandler, field_serializer, model_serializer

from vellum.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.errors import WorkflowError
from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.references.node import NodeReference
from vellum.workflows.types.generics import OutputsType

from .types import BaseEvent, default_serializer, serialize_type_encoder_with_id

if TYPE_CHECKING:
    from vellum.workflows.nodes.bases import BaseNode


class _BaseNodeExecutionBody(UniversalBaseModel):
    node_definition: Type["BaseNode"]

    @field_serializer("node_definition")
    def serialize_node_definition(self, node_definition: Type, _info: Any) -> Dict[str, Any]:
        return serialize_type_encoder_with_id(node_definition)

    # Couldn't get this to work with model_config.exclude_none or model_config.exclude_defaults
    # so we're excluding null invoked_ports manually here for now
    @model_serializer(mode="wrap", when_used="json")
    def serialize_model(self, handler: SerializerFunctionWrapHandler) -> Any:
        serialized = super().serialize_model(handler)  # type: ignore[call-arg, arg-type]
        if "invoked_ports" in serialized and serialized["invoked_ports"] is None:
            del serialized["invoked_ports"]
        return serialized


class _BaseNodeEvent(BaseEvent):
    body: _BaseNodeExecutionBody

    @property
    def node_definition(self) -> Type["BaseNode"]:
        return self.body.node_definition


NodeInputName = Union[NodeReference, AccessorExpression]
InvokedPorts = Optional[Set["Port"]]


class NodeExecutionInitiatedBody(_BaseNodeExecutionBody):
    inputs: Dict[NodeInputName, Any]

    @field_serializer("inputs")
    def serialize_inputs(self, inputs: Dict[NodeInputName, Any], _info: Any) -> Dict[str, Any]:
        return default_serializer({descriptor.name: value for descriptor, value in inputs.items()})


class NodeExecutionInitiatedEvent(_BaseNodeEvent):
    name: Literal["node.execution.initiated"] = "node.execution.initiated"
    body: NodeExecutionInitiatedBody

    @property
    def inputs(self) -> Dict[NodeInputName, Any]:
        return self.body.inputs


class NodeExecutionStreamingBody(_BaseNodeExecutionBody):
    output: BaseOutput
    invoked_ports: InvokedPorts = None

    @field_serializer("output")
    def serialize_output(self, output: BaseOutput, _info: Any) -> Dict[str, Any]:
        return default_serializer(output)

    @field_serializer("invoked_ports")
    def serialize_invoked_ports(self, invoked_ports: InvokedPorts, _info: Any) -> Optional[List[Dict[str, Any]]]:
        if not invoked_ports:
            return None
        return [default_serializer(port) for port in invoked_ports]


class NodeExecutionStreamingEvent(_BaseNodeEvent):
    name: Literal["node.execution.streaming"] = "node.execution.streaming"
    body: NodeExecutionStreamingBody

    @property
    def output(self) -> BaseOutput:
        return self.body.output

    @property
    def invoked_ports(self) -> InvokedPorts:
        return self.body.invoked_ports


class NodeExecutionFulfilledBody(_BaseNodeExecutionBody, Generic[OutputsType]):
    outputs: OutputsType
    invoked_ports: InvokedPorts = None
    mocked: Optional[bool] = None

    @field_serializer("outputs")
    def serialize_outputs(self, outputs: OutputsType, _info: Any) -> Dict[str, Any]:
        return default_serializer(outputs)

    @field_serializer("invoked_ports")
    def serialize_invoked_ports(self, invoked_ports: InvokedPorts, _info: Any) -> Optional[List[Dict[str, Any]]]:
        if invoked_ports is None:
            return None
        return [default_serializer(port) for port in invoked_ports]


class NodeExecutionFulfilledEvent(_BaseNodeEvent, Generic[OutputsType]):
    name: Literal["node.execution.fulfilled"] = "node.execution.fulfilled"
    body: NodeExecutionFulfilledBody[OutputsType]

    @property
    def outputs(self) -> OutputsType:
        return self.body.outputs

    @property
    def invoked_ports(self) -> InvokedPorts:
        return self.body.invoked_ports

    @property
    def mocked(self) -> Optional[bool]:
        return self.body.mocked


class NodeExecutionRejectedBody(_BaseNodeExecutionBody):
    error: WorkflowError


class NodeExecutionRejectedEvent(_BaseNodeEvent):
    name: Literal["node.execution.rejected"] = "node.execution.rejected"
    body: NodeExecutionRejectedBody

    @property
    def error(self) -> WorkflowError:
        return self.body.error


class NodeExecutionPausedBody(_BaseNodeExecutionBody):
    pass


class NodeExecutionPausedEvent(_BaseNodeEvent):
    name: Literal["node.execution.paused"] = "node.execution.paused"
    body: NodeExecutionPausedBody


class NodeExecutionResumedBody(_BaseNodeExecutionBody):
    pass


class NodeExecutionResumedEvent(_BaseNodeEvent):
    name: Literal["node.execution.resumed"] = "node.execution.resumed"
    body: NodeExecutionResumedBody


NodeEvent = Union[
    NodeExecutionInitiatedEvent,
    NodeExecutionStreamingEvent,
    NodeExecutionFulfilledEvent,
    NodeExecutionRejectedEvent,
    NodeExecutionPausedEvent,
    NodeExecutionResumedEvent,
]
