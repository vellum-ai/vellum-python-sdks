from datetime import datetime
import json
from uuid import UUID, uuid4
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BeforeValidator, Field, field_validator

from vellum.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.utils import datetime_now


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


def serialize_type_encoder_with_id(obj: Union[type, "CodeResourceDefinition"]) -> Dict[str, Any]:
    if hasattr(obj, "__id__") and isinstance(obj, type):
        return {
            "id": getattr(obj, "__id__"),
            **serialize_type_encoder(obj),
        }
    elif isinstance(obj, CodeResourceDefinition):
        return obj.model_dump(mode="json")

    raise AttributeError(f"The object of type '{type(obj).__name__}' must have an '__id__' attribute.")


def default_serializer(obj: Any) -> Any:
    return json.loads(
        json.dumps(
            obj,
            cls=DefaultStateEncoder,
        )
    )


class CodeResourceDefinition(UniversalBaseModel):
    id: UUID
    name: str
    module: List[str]

    @staticmethod
    def encode(obj: type) -> "CodeResourceDefinition":
        return CodeResourceDefinition(**serialize_type_encoder_with_id(obj))


VellumCodeResourceDefinition = Annotated[
    CodeResourceDefinition,
    BeforeValidator(lambda d: (d if type(d) is dict else serialize_type_encoder_with_id(d))),
]


class BaseParentContext(UniversalBaseModel):
    span_id: UUID
    parent: Optional["ParentContext"] = None
    type: str

    @field_validator("parent")
    @classmethod
    def validate_parent(cls, value: Optional[Dict[str, Any]]) -> Optional["ParentContext"]:
        if not value:
            return None

        parent_type = value.get("type")
        if parent_type not in [
            "WORKFLOW_RELEASE_TAG",
            "PROMPT_RELEASE_TAG",
            "WORKFLOW_NODE",
            "WORKFLOW",
            "WORKFLOW_SANDBOX",
            "API_REQUEST",
            "UNKNOWN",
        ]:
            value["type"] = "UNKNOWN"

        return BaseParentContext.model_validate(value)


class BaseDeploymentParentContext(BaseParentContext):
    deployment_id: UUID
    deployment_name: str
    deployment_history_item_id: UUID
    release_tag_id: UUID
    release_tag_name: str
    external_id: Optional[str]
    metadata: Optional[dict]


class WorkflowDeploymentParentContext(BaseDeploymentParentContext):
    type: Literal["WORKFLOW_RELEASE_TAG"] = "WORKFLOW_RELEASE_TAG"
    workflow_version_id: UUID


class PromptDeploymentParentContext(BaseDeploymentParentContext):
    type: Literal["PROMPT_RELEASE_TAG"] = "PROMPT_RELEASE_TAG"
    prompt_version_id: UUID


class NodeParentContext(BaseParentContext):
    type: Literal["WORKFLOW_NODE"] = "WORKFLOW_NODE"
    node_definition: VellumCodeResourceDefinition


class WorkflowParentContext(BaseParentContext):
    type: Literal["WORKFLOW"] = "WORKFLOW"
    workflow_definition: VellumCodeResourceDefinition


class WorkflowSandboxParentContext(BaseParentContext):
    type: Literal["WORKFLOW_SANDBOX"] = "WORKFLOW_SANDBOX"
    sandbox_id: UUID
    sandbox_history_item_id: UUID
    scenario_id: UUID


class APIRequestParentContext(BaseParentContext):
    type: Literal["API_REQUEST"] = "API_REQUEST"


class UnknownParentContext(BaseParentContext):
    type: Literal["UNKNOWN"] = "UNKNOWN"


# Define the discriminated union
ParentContext = Annotated[
    Union[
        WorkflowParentContext,
        NodeParentContext,
        WorkflowDeploymentParentContext,
        PromptDeploymentParentContext,
        WorkflowSandboxParentContext,
        APIRequestParentContext,
        UnknownParentContext,
    ],
    Field(discriminator="type"),
]

# Update the forward references
BaseParentContext.model_rebuild()


class BaseEvent(UniversalBaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=default_datetime_factory)
    api_version: Literal["2024-10-25"] = "2024-10-25"
    trace_id: UUID
    span_id: UUID
    parent: Optional[ParentContext] = None
