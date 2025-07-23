import importlib
import inspect
import logging
from types import FrameType
from uuid import UUID
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

import jsonschema
from pydantic import BeforeValidator

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.code_resource_definition import CodeResourceDefinition as ClientCodeResourceDefinition
from vellum.client.types.function_definition import FunctionDefinition

logger = logging.getLogger(__name__)


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

    # Enhanced metadata and parameter schema
    display_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None  # JSON Schema for parameters
    version: Optional[str] = None
    tags: Optional[List[str]] = None

    @property
    def name(self) -> str:
        """Generate a function name for this tool"""
        return self.action.lower()

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate arguments against parameter schema"""
        if not self.parameters:
            return True

        try:
            jsonschema.validate(instance=arguments, schema=self.parameters)
            return True
        except jsonschema.ValidationError as e:
            logger.warning(f"Validation failed for {self.action}: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected validation error for {self.action}: {str(e)}")
            return False

    def to_function_definition(self) -> FunctionDefinition:
        """Convert to FunctionDefinition for API compatibility"""
        return FunctionDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            forced=None,
            strict=None,
            state=None,
            cache_config=None,
        )

    @classmethod
    def from_composio_api(cls, api_response: Any) -> "ComposioToolDefinition":
        """Create instance from Composio API response"""
        # Handle both dictionary and ActionModel objects
        if hasattr(api_response, "model_dump"):
            # If it's a Pydantic model (like ActionModel), convert to dict
            response_dict = api_response.model_dump()
        elif hasattr(api_response, "__dict__"):
            # If it's an object with attributes, convert to dict
            response_dict = api_response.__dict__
        else:
            # Assume it's already a dictionary
            response_dict = api_response

        return cls(
            toolkit=response_dict.get("app_name", ""),
            action=response_dict.get("name", ""),
            description=response_dict.get("description", ""),
            display_name=response_dict.get("display_name"),
            parameters=response_dict.get("parameters", {}),
            version=response_dict.get("version"),
            tags=response_dict.get("tags", []),
        )
