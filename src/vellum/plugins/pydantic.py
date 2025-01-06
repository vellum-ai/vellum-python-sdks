from functools import lru_cache
from typing import Any, Dict, Literal, Optional, Tuple, Union

from pydantic.plugin import (
    PydanticPluginProtocol,
    SchemaKind,
    SchemaTypePath,
    ValidateJsonHandlerProtocol,
    ValidatePythonHandlerProtocol,
    ValidateStringsHandlerProtocol,
)
from pydantic_core import CoreSchema


@lru_cache(maxsize=1)
def import_base_descriptor():
    """
    We have to avoid importing from vellum.* in this file because it will cause a circular import.
    """
    from vellum.workflows.descriptors.base import BaseDescriptor

    return BaseDescriptor


# https://docs.pydantic.dev/2.8/concepts/plugins/#build-a-plugin
class OnValidatePython(ValidatePythonHandlerProtocol):
    tracked_descriptors: Dict[str, Any] = {}

    def on_enter(
        self,
        input: Any,
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
        self_instance: Optional[Any] = None,
        allow_partial: Union[bool, Literal["off", "on", "trailing-strings"]] = False,
    ) -> None:
        if not isinstance(input, dict):
            return

        self.tracked_descriptors = {}
        BaseDescriptor = import_base_descriptor()

        for key, value in input.items():
            if isinstance(value, BaseDescriptor):
                self.tracked_descriptors[key] = value
                # TODO: This does not yet work for descriptors that map to more complex types
                # https://app.shortcut.com/vellum/story/4636
                input[key] = value.types[0]()

    def on_success(self, result: Any) -> None:
        if self.tracked_descriptors:
            frozen = result.model_config.get("frozen")
            if frozen:
                result.model_config["frozen"] = False

            for key, value in self.tracked_descriptors.items():
                setattr(result, key, value)

            if frozen:
                result.model_config["frozen"] = True

            self.tracked_descriptors = {}


class VellumPydanticPlugin(PydanticPluginProtocol):
    def new_schema_validator(
        self,
        schema: CoreSchema,
        schema_type: Any,
        schema_type_path: SchemaTypePath,
        schema_kind: SchemaKind,
        config: Any,
        plugin_settings: Dict[str, Any],
    ) -> Tuple[
        Union[ValidatePythonHandlerProtocol, None],
        Union[ValidateJsonHandlerProtocol, None],
        Union[ValidateStringsHandlerProtocol, None],
    ]:
        return OnValidatePython(), None, None


pydantic_plugin = VellumPydanticPlugin()
