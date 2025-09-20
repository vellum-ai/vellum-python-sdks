import json
import os
from typing import Any, Dict, List, Type

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable import (
    APINode,
    CodeExecutionNode,
    ConditionalNode,
    ErrorNode,
    FinalOutputNode,
    GuardrailNode,
    InlinePromptNode,
    InlineSubworkflowNode,
    MapNode,
    MergeNode,
    NoteNode,
    PromptDeploymentNode,
    SearchNode,
    SubworkflowDeploymentNode,
    TemplatingNode,
    ToolCallingNode,
    WebSearchNode,
)
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext


def create_minimal_display_context() -> WorkflowDisplayContext:
    """Create a minimal WorkflowDisplayContext for serialization."""
    return WorkflowDisplayContext()


def get_all_displayable_node_classes() -> List[Type[BaseNode]]:
    """Get all displayable node classes."""
    return [
        APINode,
        CodeExecutionNode,
        ConditionalNode,
        ErrorNode,
        FinalOutputNode,
        GuardrailNode,
        InlinePromptNode,
        InlineSubworkflowNode,
        MapNode,
        MergeNode,
        NoteNode,
        PromptDeploymentNode,
        SearchNode,
        SubworkflowDeploymentNode,
        TemplatingNode,
        ToolCallingNode,
        WebSearchNode,
    ]


def serialize_node_definition(node_class: Type[BaseNode], display_context: WorkflowDisplayContext) -> Dict[str, Any]:
    """Serialize a single node definition."""
    try:
        display_class = get_node_display_class(node_class)
        display_instance = display_class()
        return display_instance.serialize(display_context)
    except Exception as e:
        print(f"Warning: Failed to serialize {node_class.__name__}: {e}")
        return {
            "id": str(node_class.__name__),
            "label": node_class.__name__,
            "type": "GENERIC",
            "error": f"Failed to serialize: {str(e)}",
        }


def main() -> None:
    """Main function to generate node definitions."""
    print("Generating node definitions...")

    display_context = create_minimal_display_context()
    node_classes = get_all_displayable_node_classes()

    node_definitions = []
    for node_class in node_classes:
        print(f"Serializing {node_class.__name__}...")
        definition = serialize_node_definition(node_class, display_context)
        node_definitions.append(definition)

    output_path = "src/vellum/workflows/assets/node-definitions.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(node_definitions, f, indent=2)

    print(f"Generated {len(node_definitions)} node definitions in {output_path}")


if __name__ == "__main__":
    main()
