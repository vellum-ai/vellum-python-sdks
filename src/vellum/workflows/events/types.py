from datetime import datetime
import json
from uuid import UUID, uuid4
from typing import Annotated, Any, Dict, List, Literal, Optional, Union, get_args

from pydantic import BeforeValidator, Field, GetCoreSchemaHandler, Tag, ValidationInfo
from pydantic_core import CoreSchema, core_schema

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


def _cast_parent_context_discriminator(v: Any) -> Any:
    if v in PARENT_CONTEXT_TYPES:
        return v

    return "UNKNOWN"


def _get_parent_context_discriminator(v: Any) -> Any:
    if isinstance(v, dict) and "type" in v:
        return _cast_parent_context_discriminator(v["type"])

    if isinstance(v, PARENT_CONTEXT_CHOICES):
        return v.type

    return _cast_parent_context_discriminator(v)


def _tag_parent_context_discriminator(v: Any) -> Any:
    return Tag(_get_parent_context_discriminator(v))


def _validate_parent_context_discriminator(v: Any, info: ValidationInfo) -> Any:
    if isinstance(v, str):
        return _get_parent_context_discriminator(v)

    if isinstance(v, dict) and "type" in v:
        v["type"] = _get_parent_context_discriminator(v["type"])

    return v


class ParentContextDiscriminator:
    def __get_pydantic_core_schema__(self, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        original_schema = handler(source_type)
        tagged_union_choices = {}
        for index, choice in enumerate(original_schema["choices"]):
            tagged_union_choices[Tag(PARENT_CONTEXT_TYPES[index])] = choice

        tagged_union_schema = core_schema.tagged_union_schema(
            tagged_union_choices,
            _tag_parent_context_discriminator,
        )
        return core_schema.with_info_before_validator_function(
            function=_validate_parent_context_discriminator,
            schema=tagged_union_schema,
            field_name="type",
        )


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
    ParentContextDiscriminator(),
]
PARENT_CONTEXT_CHOICES = get_args(get_args(ParentContext)[0])
PARENT_CONTEXT_TYPES = [
    pc.model_fields["type"].default for pc in PARENT_CONTEXT_CHOICES if issubclass(pc, UniversalBaseModel)
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
