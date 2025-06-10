from typing import Optional

from vellum.workflows.references import EnvironmentVariableReference


class EnvironmentVariables:
    @staticmethod
    def get(name: str, default: Optional[str] = None):
        env_ref = EnvironmentVariableReference(name=name)
        if default is not None:
            return env_ref.coalesce(default)
        return env_ref


# Deprecated: Use EnvironmentVariables instead. Will be removed in v0.15.0
Environment = EnvironmentVariables
