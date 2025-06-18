from uuid import UUID
from typing import Any, Dict, List, Optional


class DynamicSchemaProcessor:
    """Processes JSON schemas to replace dynamic enum markers with actual workflow node references."""

    DYNAMIC_ENUM_PATTERNS = {
        "$WORKFLOW_NODES": "workflow_nodes",
        "$TARGET_NODES": "target_nodes",
        "$SOURCE_NODES": "source_nodes",
    }

    def __init__(self, workflow_nodes: List[Any], current_node_id: UUID):
        self.workflow_nodes = workflow_nodes
        self.current_node_id = current_node_id

    def process_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Process a JSON schema and replace dynamic enum markers with actual values."""
        if not isinstance(schema, dict):
            return schema

        processed_schema: Dict[str, Any] = {}
        for key, value in schema.items():
            if key == "enum" and isinstance(value, list):
                processed_schema[key] = self._process_enum_values(value)
            elif isinstance(value, dict):
                processed_schema[key] = self.process_schema(value)
            elif isinstance(value, list):
                processed_schema[key] = [
                    self.process_schema(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                processed_schema[key] = value

        return processed_schema

    def _process_enum_values(self, enum_values: List[Any]) -> List[Any]:
        """Process enum values, replacing dynamic markers with actual node references."""
        processed_values = []

        for value in enum_values:
            if isinstance(value, str) and value in self.DYNAMIC_ENUM_PATTERNS:
                node_refs = self._get_node_references(value)
                processed_values.extend(node_refs)
            else:
                processed_values.append(value)

        return processed_values

    def _get_node_references(self, pattern: str) -> List[str]:
        """Get node references based on the dynamic pattern."""
        if pattern == "$WORKFLOW_NODES":
            return [str(node.__id__) for node in self.workflow_nodes if node.__id__ != self.current_node_id]
        elif pattern == "$TARGET_NODES":
            return self._get_target_node_ids()
        elif pattern == "$SOURCE_NODES":
            return self._get_source_node_ids()
        else:
            return []

    def _get_target_node_ids(self) -> List[str]:
        """Get IDs of nodes that this node can target (connected via edges)."""
        return [str(node.__id__) for node in self.workflow_nodes if node.__id__ != self.current_node_id]

    def _get_source_node_ids(self) -> List[str]:
        """Get IDs of nodes that can source to this node."""
        return [str(node.__id__) for node in self.workflow_nodes if node.__id__ != self.current_node_id]


def process_dynamic_json_schema(
    custom_parameters: Optional[Dict[str, Any]], workflow_nodes: List[Any], current_node_id: UUID
) -> Optional[Dict[str, Any]]:
    """Process custom parameters to handle dynamic JSON schema enum values."""
    if not custom_parameters or "json_schema" not in custom_parameters:
        return custom_parameters

    json_schema = custom_parameters.get("json_schema")
    if not isinstance(json_schema, dict) or "schema" not in json_schema:
        return custom_parameters

    processor = DynamicSchemaProcessor(workflow_nodes, current_node_id)
    processed_schema = processor.process_schema(json_schema["schema"])

    updated_parameters = custom_parameters.copy()
    updated_parameters["json_schema"] = {**json_schema, "schema": processed_schema}

    return updated_parameters
