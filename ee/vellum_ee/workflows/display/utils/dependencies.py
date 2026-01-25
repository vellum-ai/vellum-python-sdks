from typing import Dict, List, Optional, Tuple

from vellum.workflows.types.core import JsonArray, JsonObject

MODEL_PREFIX_TO_HOSTING_INTERFACE: Dict[str, Tuple[str, str]] = {
    "gpt-": ("OPENAI", "OpenAI"),
    "o1-": ("OPENAI", "OpenAI"),
    "o3-": ("OPENAI", "OpenAI"),
    "o4-": ("OPENAI", "OpenAI"),
    "text-davinci-": ("OPENAI", "OpenAI"),
    "text-embedding-": ("OPENAI", "OpenAI"),
    "davinci-": ("OPENAI", "OpenAI"),
    "curie-": ("OPENAI", "OpenAI"),
    "babbage-": ("OPENAI", "OpenAI"),
    "ada-": ("OPENAI", "OpenAI"),
    "claude-": ("ANTHROPIC", "Anthropic"),
    "gemini-": ("GOOGLE", "Google"),
    "mistral-": ("MISTRAL_AI", "Mistral AI"),
    "mixtral-": ("MISTRAL_AI", "Mistral AI"),
    "codestral-": ("MISTRAL_AI", "Mistral AI"),
    "pixtral-": ("MISTRAL_AI", "Mistral AI"),
    "deepseek-": ("DEEP_SEEK", "DeepSeek"),
    "grok-": ("X_AI", "xAI"),
    "llama-": ("META", "Meta"),
    "llama2-": ("META", "Meta"),
    "llama3-": ("META", "Meta"),
    "llama4-": ("META", "Meta"),
    "command-": ("COHERE", "Cohere"),
    "embed-": ("COHERE", "Cohere"),
    "palm-": ("GOOGLE", "Google"),
    "titan-": ("AWS_BEDROCK", "AWS Bedrock"),
    "nova-": ("AWS_BEDROCK", "AWS Bedrock"),
    "phi-": ("AZURE_AI_FOUNDRY", "Azure AI Foundry"),
    "qwen-": ("ALIBABA", "Alibaba"),
}


def infer_model_hosting_interface(model_name: str) -> Optional[Tuple[str, str]]:
    """
    Infer the hosting interface and label from a model name.

    Args:
        model_name: The name of the ML model (e.g., "gpt-4o", "claude-3-opus")

    Returns:
        A tuple of (hosting_interface, label) if the model can be mapped,
        None otherwise.
    """
    model_name_lower = model_name.lower()
    for prefix, (hosting_interface, label) in MODEL_PREFIX_TO_HOSTING_INTERFACE.items():
        if model_name_lower.startswith(prefix):
            return (hosting_interface, label)
    return None


def extract_model_provider_dependencies(serialized_nodes: List[JsonObject]) -> JsonArray:
    """
    Extract model provider dependencies from serialized workflow nodes.

    Args:
        serialized_nodes: List of serialized node dictionaries

    Returns:
        List of WorkflowModelProviderDependency dictionaries
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

        if ml_model_name in seen_models:
            continue

        hosting_info = infer_model_hosting_interface(ml_model_name)
        if hosting_info is None:
            continue

        hosting_interface, label = hosting_info
        seen_models[ml_model_name] = {
            "type": "MODEL_PROVIDER",
            "name": hosting_interface,
            "label": label,
            "model_name": ml_model_name,
        }

    return list(seen_models.values())
