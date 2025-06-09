from typing import Optional

from vellum.workflows.references import EnvironmentVariableReference


class EnvironmentVariables:
    @staticmethod
    def get(name: str, default: Optional[str] = None) -> EnvironmentVariableReference:
        return EnvironmentVariableReference(name=name, default=default)


# Deprecated: Use EnvironmentVariables instead. Will be removed in v0.15.0
Environment = EnvironmentVariables
