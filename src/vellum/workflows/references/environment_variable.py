import os
from typing import TYPE_CHECKING, Optional

from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState


class EnvironmentVariableReference(BaseDescriptor[str]):
    def __init__(self, *, name: str, default: Optional[str] = None):
        super().__init__(name=name, types=(str,))
        self._default = default

    def resolve(self, state: "BaseState") -> str:
        if hasattr(state, "context") and hasattr(state.context, "environment_variables"):
            context_env_value = state.context.environment_variables.get(self.name)
            if context_env_value is not None:
                return context_env_value
        env_value = os.environ.get(self.name)
        if env_value is not None:
            return env_value

        if self._default is not None:
            return self._default

        return ""
