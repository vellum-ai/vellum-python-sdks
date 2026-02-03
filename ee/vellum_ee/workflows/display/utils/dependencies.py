import ast
from enum import Enum
import inspect
import textwrap
from typing import List, NamedTuple, Optional, Type

from vellum.client.core.pydantic_utilities import UniversalBaseModel


class IntegrationDependency(NamedTuple):
    provider: str
    integration_name: str


def extract_integration_dependencies_from_node(node_class: Type) -> List[IntegrationDependency]:
    """
    Extract integration dependencies from a node's run method by parsing calls to execute_integration_tool.

    This function inspects the source code of the node's run method and looks for calls to
    `execute_integration_tool` (typically via `self._context.vellum_client.integrations.execute_integration_tool`
    or `client.integrations.execute_integration_tool`).

    Args:
        node_class: The node class to inspect

    Returns:
        A list of IntegrationDependency tuples containing (provider, integration_name)
    """
    dependencies: List[IntegrationDependency] = []

    run_method = getattr(node_class, "run", None)
    if run_method is None:
        return dependencies

    try:
        source = inspect.getsource(run_method)
        source = textwrap.dedent(source)
    except (OSError, TypeError):
        return dependencies

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return dependencies

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        integration_dep = _extract_integration_from_call(node)
        if integration_dep:
            dependencies.append(integration_dep)

    return dependencies


def _extract_integration_from_call(call_node: ast.Call) -> Optional[IntegrationDependency]:
    """
    Extract integration dependency from an AST Call node if it's a call to execute_integration_tool.
    """
    if not _is_execute_integration_tool_call(call_node):
        return None

    integration_name = _extract_keyword_string_value(call_node, "integration_name")
    integration_provider = _extract_keyword_string_value(call_node, "integration_provider")

    if integration_name and integration_provider:
        return IntegrationDependency(provider=integration_provider, integration_name=integration_name)

    return None


def _is_execute_integration_tool_call(call_node: ast.Call) -> bool:
    """
    Check if the call node is a call to execute_integration_tool.
    Handles patterns like:
    - client.integrations.execute_integration_tool(...)
    - self._context.vellum_client.integrations.execute_integration_tool(...)
    """
    func = call_node.func

    if isinstance(func, ast.Attribute) and func.attr == "execute_integration_tool":
        return True

    return False


def _extract_keyword_string_value(call_node: ast.Call, keyword_name: str) -> Optional[str]:
    """
    Extract the string value of a keyword argument from a call node.
    """
    for keyword in call_node.keywords:
        if keyword.arg == keyword_name:
            if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                return keyword.value.value
    return None


class MLModelHostingInterface(str, Enum):
    """
    Enum representing the hosting interface for ML models.
    This will be replaced by a generated enum from the client in the future.
    """

    ANTHROPIC = "ANTHROPIC"
    AWS_BEDROCK = "AWS_BEDROCK"
    AZURE_OPENAI = "AZURE_OPENAI"
    COHERE = "COHERE"
    FIREWORKS = "FIREWORKS"
    GOOGLE = "GOOGLE"
    GROQ = "GROQ"
    MISTRAL = "MISTRAL"
    OPENAI = "OPENAI"


class MLModel(UniversalBaseModel):
    """
    Represents an ML model with its name and hosting interface.
    """

    name: str
    hosted_by: MLModelHostingInterface
