import os
from typing import TYPE_CHECKING

from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState


class EnvironmentVariableReference(BaseDescriptor[str]):
    def __init__(self, *, name: str) -> None:
        super().__init__(name=name, types=(str,))

    def resolve(self, state: "BaseState") -> str:
        env_value = os.environ.get(self.name)
        if env_value is not None:
            return env_value

        # Fetch Vellum Environment Variable named `self.name` once that project is done
        raise ValueError(f"No environment variable named '{self.name}' found")
