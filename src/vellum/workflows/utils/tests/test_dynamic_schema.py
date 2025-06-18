from unittest.mock import Mock
from uuid import uuid4
from typing import Any, Dict, List

from vellum.workflows.utils.dynamic_schema import DynamicSchemaProcessor, process_dynamic_json_schema


class TestDynamicSchemaProcessor:
    def test_process_schema_with_workflow_nodes_enum(self):
        mock_node1 = Mock()
        mock_node1.__id__ = uuid4()
        mock_node2 = Mock()
        mock_node2.__id__ = uuid4()
        current_node_id = uuid4()

        workflow_nodes = [mock_node1, mock_node2]
        processor = DynamicSchemaProcessor(workflow_nodes, current_node_id)

        schema = {"type": "object", "properties": {"next": {"type": "string", "enum": ["$WORKFLOW_NODES"]}}}

        result = processor.process_schema(schema)

        expected_enum = [str(mock_node1.__id__), str(mock_node2.__id__)]
        assert result["properties"]["next"]["enum"] == expected_enum

    def test_process_schema_with_mixed_enum_values(self):
        mock_node1 = Mock()
        mock_node1.__id__ = uuid4()
        current_node_id = uuid4()

        workflow_nodes = [mock_node1]
        processor = DynamicSchemaProcessor(workflow_nodes, current_node_id)

        schema = {
            "type": "object",
            "properties": {"action": {"type": "string", "enum": ["FINISH", "$WORKFLOW_NODES", "RESTART"]}},
        }

        result = processor.process_schema(schema)

        expected_enum = ["FINISH", str(mock_node1.__id__), "RESTART"]
        assert result["properties"]["action"]["enum"] == expected_enum

    def test_process_schema_without_dynamic_enums(self):
        workflow_nodes: List[Any] = []
        processor = DynamicSchemaProcessor(workflow_nodes, uuid4())

        schema = {"type": "object", "properties": {"status": {"type": "string", "enum": ["SUCCESS", "FAILURE"]}}}

        result = processor.process_schema(schema)

        assert result["properties"]["status"]["enum"] == ["SUCCESS", "FAILURE"]

    def test_excludes_current_node_from_workflow_nodes(self):
        current_node_id = uuid4()
        mock_node1 = Mock()
        mock_node1.__id__ = current_node_id
        mock_node2 = Mock()
        mock_node2.__id__ = uuid4()

        workflow_nodes = [mock_node1, mock_node2]
        processor = DynamicSchemaProcessor(workflow_nodes, current_node_id)

        schema = {"type": "object", "properties": {"next": {"type": "string", "enum": ["$WORKFLOW_NODES"]}}}

        result = processor.process_schema(schema)

        assert result["properties"]["next"]["enum"] == [str(mock_node2.__id__)]

    def test_process_nested_schema_structures(self):
        mock_node1 = Mock()
        mock_node1.__id__ = uuid4()
        current_node_id = uuid4()

        workflow_nodes = [mock_node1]
        processor = DynamicSchemaProcessor(workflow_nodes, current_node_id)

        schema = {
            "type": "object",
            "properties": {
                "routing": {
                    "type": "object",
                    "properties": {"next_node": {"type": "string", "enum": ["$WORKFLOW_NODES"]}},
                }
            },
        }

        result = processor.process_schema(schema)

        assert result["properties"]["routing"]["properties"]["next_node"]["enum"] == [str(mock_node1.__id__)]

    def test_process_schema_with_target_nodes_pattern(self):
        mock_node1 = Mock()
        mock_node1.__id__ = uuid4()
        current_node_id = uuid4()

        workflow_nodes = [mock_node1]
        processor = DynamicSchemaProcessor(workflow_nodes, current_node_id)

        schema = {"type": "object", "properties": {"target": {"type": "string", "enum": ["$TARGET_NODES"]}}}

        result = processor.process_schema(schema)

        assert result["properties"]["target"]["enum"] == [str(mock_node1.__id__)]

    def test_process_schema_with_source_nodes_pattern(self):
        mock_node1 = Mock()
        mock_node1.__id__ = uuid4()
        current_node_id = uuid4()

        workflow_nodes = [mock_node1]
        processor = DynamicSchemaProcessor(workflow_nodes, current_node_id)

        schema = {"type": "object", "properties": {"source": {"type": "string", "enum": ["$SOURCE_NODES"]}}}

        result = processor.process_schema(schema)

        assert result["properties"]["source"]["enum"] == [str(mock_node1.__id__)]


class TestProcessDynamicJsonSchema:
    def test_process_with_json_schema_parameter(self):
        mock_node = Mock()
        mock_node.__id__ = uuid4()
        current_node_id = uuid4()

        custom_parameters = {
            "json_schema": {
                "name": "test_schema",
                "schema": {"type": "object", "properties": {"next": {"type": "string", "enum": ["$WORKFLOW_NODES"]}}},
            }
        }

        result = process_dynamic_json_schema(
            custom_parameters=custom_parameters, workflow_nodes=[mock_node], current_node_id=current_node_id
        )

        assert result is not None
        assert result["json_schema"]["schema"]["properties"]["next"]["enum"] == [str(mock_node.__id__)]

    def test_process_without_json_schema_parameter(self):
        custom_parameters = {"temperature": 0.7}

        result = process_dynamic_json_schema(
            custom_parameters=custom_parameters, workflow_nodes=[], current_node_id=uuid4()
        )

        assert result == custom_parameters

    def test_process_with_none_parameters(self):
        result = process_dynamic_json_schema(custom_parameters=None, workflow_nodes=[], current_node_id=uuid4())

        assert result is None

    def test_process_with_empty_json_schema(self):
        custom_parameters: Dict[str, Any] = {"json_schema": {}}

        result = process_dynamic_json_schema(
            custom_parameters=custom_parameters, workflow_nodes=[], current_node_id=uuid4()
        )

        assert result == custom_parameters

    def test_process_preserves_other_json_schema_fields(self):
        mock_node = Mock()
        mock_node.__id__ = uuid4()
        current_node_id = uuid4()

        custom_parameters = {
            "json_schema": {
                "name": "test_schema",
                "description": "A test schema",
                "schema": {"type": "object", "properties": {"next": {"type": "string", "enum": ["$WORKFLOW_NODES"]}}},
            }
        }

        result = process_dynamic_json_schema(
            custom_parameters=custom_parameters, workflow_nodes=[mock_node], current_node_id=current_node_id
        )

        assert result is not None
        assert result["json_schema"]["name"] == "test_schema"
        assert result["json_schema"]["description"] == "A test schema"
        assert result["json_schema"]["schema"]["properties"]["next"]["enum"] == [str(mock_node.__id__)]
