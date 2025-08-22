import importlib
import inspect
from types import FrameType
from uuid import UUID
from typing import Annotated, Any, Dict, Literal, Optional, Union

from pydantic import BeforeValidator

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.code_resource_definition import CodeResourceDefinition as ClientCodeResourceDefinition
from vellum.workflows.constants import AuthorizationType
from vellum.workflows.references.environment_variable import EnvironmentVariableReference


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
