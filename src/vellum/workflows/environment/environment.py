from vellum.workflows.references import EnvironmentVariableReference


class Environment:
    @staticmethod
    def get(name: str) -> EnvironmentVariableReference:
        return EnvironmentVariableReference(name=name)

    @staticmethod
    def get_or(name: str, default: str) -> EnvironmentVariableReference:
        return EnvironmentVariableReference(name=name, default=default)
