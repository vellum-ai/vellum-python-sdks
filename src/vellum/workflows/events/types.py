from datetime import datetime
from enum import Enum
import json
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Type, Union

from pydantic import Field, field_serializer

from vellum.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.utils import datetime_now

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow
    from vellum.workflows.nodes import BaseNode


class WorkflowEventType(Enum):
    NODE = "NODE"
    WORKFLOW = "WORKFLOW"


def default_datetime_factory() -> datetime:
    """
    Makes it possible to mock the datetime factory for testing.
    """

    return datetime_now()


excluded_modules = {"typing", "builtins"}


def serialize_type_encoder(obj: type) -> Dict[str, Any]:
    return {
        "name": obj.__name__,
        "module": obj.__module__.split("."),
    }


def default_serializer(obj: Any) -> Any:
    return json.loads(
        json.dumps(
            obj,
            cls=DefaultStateEncoder,
        )
    )


class BaseParentContext(UniversalBaseModel):
    span_id: UUID
    parent: Optional['ParentContext'] = None


class BaseDeploymentParentContext(BaseParentContext):
    deployment_id: UUID
    deployment_name: str
    deployment_history_item_id: UUID
    release_tag_id: UUID
    release_tag_name: str
    external_id: Optional[str]


class WorkflowDeploymentParentContext(BaseDeploymentParentContext):
    type: Literal["WORKFLOW_RELEASE_TAG"] = "WORKFLOW_RELEASE_TAG"
    workflow_version_id: UUID


class PromptDeploymentParentContext(BaseDeploymentParentContext):
    type: Literal["PROMPT_RELEASE_TAG"] = "PROMPT_RELEASE_TAG"
    prompt_version_id: UUID


class NodeParentContext(BaseParentContext):
    type: Literal["WORKFLOW_NODE"] = "WORKFLOW_NODE"
    node_definition: Type['BaseNode']

    @field_serializer("node_definition")
    def serialize_node_definition(self, definition: Type, _info: Any) -> Dict[str, Any]:
        return serialize_type_encoder(definition)


class WorkflowParentContext(BaseParentContext):
    type: Literal["WORKFLOW"] = "WORKFLOW"
    workflow_definition: Type['BaseWorkflow']

    @field_serializer("workflow_definition")
    def serialize_workflow_definition(self, definition: Type, _info: Any) -> Dict[str, Any]:
        return serialize_type_encoder(definition)


ParentContext = Union[
    NodeParentContext,
    WorkflowParentContext,
    PromptDeploymentParentContext,
    WorkflowDeploymentParentContext,
]


class BaseEvent(UniversalBaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=default_datetime_factory)
    api_version: Literal["2024-10-25"] = "2024-10-25"
    trace_id: UUID
    span_id: UUID
    parent: Optional[ParentContext] = None
