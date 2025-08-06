import os
from typing import TYPE_CHECKING, Any, Optional

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState


class EnvironmentVariableReference(BaseDescriptor[str]):
    def __init__(
        self,
        *,
        name: str,
        # DEPRECATED - to be removed in 0.15.0 release
        default: Optional[str] = None,
        serialize_as_constant: bool = False,
    ):
        super().__init__(name=name, types=(str,))
        self._serialize_as_constant = serialize_as_constant

    def resolve(self, state: "BaseState") -> Any:
        env_value = os.environ.get(self.name)
        if env_value is not None:
            return env_value

        return undefined

    @property
    def serialize_as_constant(self) -> bool:
        return self._serialize_as_constant

    @serialize_as_constant.setter
    def serialize_as_constant(self, value: bool):
        self._serialize_as_constant = value
