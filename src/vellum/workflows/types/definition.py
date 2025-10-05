import importlib
import inspect
from types import FrameType
from uuid import UUID
from typing import TYPE_CHECKING, Annotated, Any, Callable, Dict, List, Literal, Optional, Type, Union

from pydantic import BeforeValidator, SerializationInfo, model_serializer

from vellum import Vellum
from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.code_resource_definition import CodeResourceDefinition as ClientCodeResourceDefinition
from vellum.client.types.vellum_variable import VellumVariable
from vellum.workflows.constants import AuthorizationType, VellumIntegrationProviderType
from vellum.workflows.references.environment_variable import EnvironmentVariableReference

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow


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


class CodeResourceDefinition(ClientCodeResourceDefinition):
    id: UUID

    @staticmethod
    def encode(obj: type) -> "CodeResourceDefinition":
        return CodeResourceDefinition(**serialize_type_encoder_with_id(obj))

    def decode(self) -> Any:
        if ".<locals>." in self.name:
            # We are decoding a local class that should already be loaded in our stack frame. So
            # we climb up to look for it.
            frame = inspect.currentframe()
            return self._resolve_local(frame)

        try:
            imported_module = importlib.import_module(".".join(self.module))
        except ImportError:
            return None

        return getattr(imported_module, self.name, None)

    def _resolve_local(self, frame: Optional[FrameType]) -> Any:
        if not frame:
            return None

        frame_module = frame.f_globals.get("__name__")
        if not isinstance(frame_module, str) or frame_module.split(".") != self.module:
            return self._resolve_local(frame.f_back)

        outer, inner = self.name.split(".<locals>.")
        frame_outer = frame.f_code.co_name
        if frame_outer != outer:
            return self._resolve_local(frame.f_back)

        return frame.f_locals.get(inner)


VellumCodeResourceDefinition = Annotated[
    CodeResourceDefinition,
    BeforeValidator(lambda d: (d if type(d) is dict else serialize_type_encoder_with_id(d))),
]


class DeploymentDefinition(UniversalBaseModel):
    deployment: str
    release_tag: str = "LATEST"

    # hydrated fields
    name: Optional[str] = None
    description: Optional[str] = None
    input_variables: Optional[List[VellumVariable]] = None

    def _is_uuid(self) -> bool:
        """Check if the deployment field is a valid UUID."""
        try:
            UUID(self.deployment)
            return True
        except ValueError:
            return False

    @property
    def deployment_id(self) -> Optional[UUID]:
        """Get the deployment ID if the deployment field is a UUID."""
        if self._is_uuid():
            return UUID(self.deployment)
        return None

    @property
    def deployment_name(self) -> Optional[str]:
        """Get the deployment name if the deployment field is not a UUID."""
        if not self._is_uuid():
            return self.deployment
        return None

    def get_release_info(self, client: Vellum):
        try:
            release = client.workflow_deployments.retrieve_workflow_deployment_release(
                self.deployment, self.release_tag
            )
        except Exception:
            # If we fail to get the release info, we'll use the deployment name and description
            return {
                "name": self.deployment,
                "description": f"Workflow Deployment for {self.deployment}",
                "input_variables": [],
            }

        return {
            "name": release.deployment.name,
            "description": release.description or f"Workflow Deployment for {self.deployment}",
            "input_variables": release.workflow_version.input_variables,
        }

    @model_serializer(mode="wrap")
    def _serialize(self, handler, info: SerializationInfo):
        """Allow Pydantic to serialize directly given a `client` in context.

        Falls back to the default serialization when client is not provided.
        """
        context = info.context if info and hasattr(info, "context") else {}
        client: Optional[Vellum] = context.get("client") if context else None

        if client:
            release_info = self.get_release_info(client)
            return {
                "type": "WORKFLOW_DEPLOYMENT",
                "name": release_info["name"],
                "description": release_info["description"],
                "deployment": self.deployment,
                "release_tag": self.release_tag,
            }

        return handler(self)


class ComposioToolDefinition(UniversalBaseModel):
    """Represents a specific Composio action that can be used in Tool Calling Node"""

    type: Literal["COMPOSIO"] = "COMPOSIO"

    # Core identification
    toolkit: str  # "GITHUB", "SLACK", etc.
    action: str  # Specific action like "GITHUB_CREATE_AN_ISSUE"
    description: str
    user_id: Optional[str] = None
    name: str = ""

    def model_post_init(self, __context: Any):
        if self.name == "":
            self.name = self.action.lower()


class VellumIntegrationToolDefinition(UniversalBaseModel):
    type: Literal["VELLUM_INTEGRATION"] = "VELLUM_INTEGRATION"

    # Core identification
    provider: VellumIntegrationProviderType
    integration_name: str  # "GITHUB", "SLACK", etc.
    name: str  # Specific action like "GITHUB_CREATE_AN_ISSUE"

    # Required for tool base consistency
    description: str


class VellumIntegrationToolDetails(VellumIntegrationToolDefinition):
    """Extended version of VellumIntegrationToolDefinition with runtime parameters.

    This class includes the parameters field which is populated during compilation
    from the Vellum integrations API response. It inherits all fields from the base
    VellumIntegrationToolDefinition class.
    """

    parameters: Optional[Dict[str, Any]] = None


class MCPServer(UniversalBaseModel):
    type: Literal["MCP_SERVER"] = "MCP_SERVER"
    name: str
    description: str = ""  # We don't use this field, its for compatibility with UI
    url: str
    authorization_type: Optional[AuthorizationType] = None
    bearer_token_value: Optional[Union[str, EnvironmentVariableReference]] = None
    api_key_header_key: Optional[str] = None
    api_key_header_value: Optional[Union[str, EnvironmentVariableReference]] = None

    model_config = {"arbitrary_types_allowed": True}

    def __setattr__(self, name: str, value: Any) -> None:
        """Override to automatically set serialization flags for environment variables."""
        super().__setattr__(name, value)

        if name == "bearer_token_value" and isinstance(value, EnvironmentVariableReference):
            value.serialize_as_constant = True

        if name == "api_key_header_value" and isinstance(value, EnvironmentVariableReference):
            value.serialize_as_constant = True


class MCPToolDefinition(UniversalBaseModel):
    name: str
    server: MCPServer
    description: Optional[str] = None
    parameters: Dict[str, Any] = {}


# Type alias for functions that can be called in tool calling nodes
ToolBase = Union[
    Callable[..., Any],
    DeploymentDefinition,
    Type["BaseWorkflow"],
    ComposioToolDefinition,
    VellumIntegrationToolDefinition,
]
Tool = Union[ToolBase, MCPServer]
