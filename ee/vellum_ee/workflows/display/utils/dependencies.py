from enum import Enum
from typing import Dict, List

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.types.core import JsonArray, JsonObject


class MLModelHostingInterface(str, Enum):
    """
    Enum representing the hosting interface for ML models.
    This will be replaced by a generated enum from the client in the future.
    """

    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GOOGLE = "GOOGLE"
    AZURE_OPENAI = "AZURE_OPENAI"
    AWS_BEDROCK = "AWS_BEDROCK"
    FIREWORKS = "FIREWORKS"
    GROQ = "GROQ"
    MISTRAL = "MISTRAL"
    COHERE = "COHERE"


class MLModel(UniversalBaseModel):
    """
    Represents an ML model with its name and hosting interface.
    """

    name: str
    hosted_by: MLModelHostingInterface


def extract_model_provider_dependencies(serialized_nodes: List[JsonObject], ml_models: List[MLModel]) -> JsonArray:
    """
    Extract model provider dependencies from serialized workflow nodes.

    Args:
        serialized_nodes: List of serialized node dictionaries
        ml_models: List of MLModel objects containing name to hosting interface mappings

    Returns:
        List of WorkflowModelProviderDependency dictionaries, sorted alphabetically
        by (name, model_name) for deterministic output.
    """
    model_lookup: Dict[str, MLModelHostingInterface] = {model.name: model.hosted_by for model in ml_models}
    seen_models: Dict[str, JsonObject] = {}

    for node in serialized_nodes:
        if not isinstance(node, dict):
            continue

        node_type = node.get("type")
        if node_type != "PROMPT":
            continue

        data = node.get("data")
        if not isinstance(data, dict):
            continue

        ml_model_name = data.get("ml_model_name")
        if not ml_model_name or not isinstance(ml_model_name, str):
            continue

        if ml_model_name in seen_models:
            continue

        hosting_interface = model_lookup.get(ml_model_name)
        if hosting_interface is None:
            continue

        seen_models[ml_model_name] = {
            "type": "MODEL_PROVIDER",
            "name": hosting_interface.value,
            "model_name": ml_model_name,
        }

    dependencies: JsonArray = list(seen_models.values())

    def sort_key(d: object) -> tuple:
        if isinstance(d, dict):
            return (str(d.get("name", "")), str(d.get("model_name", "")))
        return ("", "")

    dependencies.sort(key=sort_key)  # type: ignore[arg-type]
    return dependencies
