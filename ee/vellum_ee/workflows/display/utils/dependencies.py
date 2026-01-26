from typing import Dict, List, Optional, Tuple

from vellum.workflows.types.core import JsonArray, JsonObject

# Type alias for the model prefix to hosting interface mapping
# Maps model name prefixes to (hosting_interface, label) tuples
ModelPrefixMapping = Dict[str, Tuple[str, str]]


def infer_model_hosting_interface(model_name: str, prefix_map: ModelPrefixMapping) -> Optional[Tuple[str, str]]:
    """
    Infer the hosting interface and label from a model name using the provided mapping.

    Args:
        model_name: The name of the ML model (e.g., "gpt-4o", "claude-3-opus")
        prefix_map: Mapping of model name prefixes to (hosting_interface, label) tuples

    Returns:
        A tuple of (hosting_interface, label) if the model can be mapped,
        None otherwise.
    """
    model_name_lower = model_name.lower()
    for prefix, (hosting_interface, label) in prefix_map.items():
        if model_name_lower.startswith(prefix):
            return (hosting_interface, label)
    return None


def extract_model_provider_dependencies(
    serialized_nodes: List[JsonObject], prefix_map: ModelPrefixMapping
) -> JsonArray:
    """
    Extract model provider dependencies from serialized workflow nodes.

    Args:
        serialized_nodes: List of serialized node dictionaries
        prefix_map: Mapping of model name prefixes to (hosting_interface, label) tuples

    Returns:
        List of WorkflowModelProviderDependency dictionaries, sorted alphabetically
        by (name, model_name) for deterministic output.
    """
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

        model_key = ml_model_name.lower()
        if model_key in seen_models:
            continue

        hosting_info = infer_model_hosting_interface(ml_model_name, prefix_map)
        if hosting_info is None:
            continue

        hosting_interface, label = hosting_info
        seen_models[model_key] = {
            "type": "MODEL_PROVIDER",
            "name": hosting_interface,
            "label": label,
            "model_name": ml_model_name,
        }

    dependencies: JsonArray = list(seen_models.values())

    def sort_key(d: object) -> tuple:
        if isinstance(d, dict):
            return (str(d.get("name", "")), str(d.get("model_name", "")))
        return ("", "")

    dependencies.sort(key=sort_key)  # type: ignore[arg-type]
    return dependencies
