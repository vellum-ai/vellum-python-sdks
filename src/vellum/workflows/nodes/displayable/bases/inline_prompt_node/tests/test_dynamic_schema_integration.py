from unittest.mock import Mock, patch
from uuid import uuid4

from vellum import PromptParameters
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.node import BaseInlinePromptNode
from vellum.workflows.state.base import BaseState, StateMeta


class TestDynamicSchemaIntegration:
    def test_process_parameters_for_dynamic_schema_with_workflow_nodes(self):
        mock_node1 = Mock()
        mock_node1.__id__ = uuid4()
        mock_node2 = Mock()
        mock_node2.__id__ = uuid4()
        current_node_id = uuid4()

        mock_workflow = Mock()
        mock_workflow.get_nodes.return_value = [mock_node1, mock_node2]

        state = BaseState()
        state.meta = StateMeta(workflow_definition=mock_workflow)

        custom_parameters = {
            "json_schema": {
                "name": "WorkflowRouter",
                "schema": {
                    "type": "object",
                    "properties": {"next_step": {"type": "string", "enum": ["$WORKFLOW_NODES", "END"]}},
                },
            }
        }

        parameters = PromptParameters(custom_parameters=custom_parameters)

        class TestPromptNode(BaseInlinePromptNode):
            ml_model = "test-model"
            blocks = []

        node = TestPromptNode()
        node.state = state
        node.__id__ = current_node_id
        node.parameters = parameters

        result = node._process_parameters_for_dynamic_schema()

        expected_enum = [str(mock_node1.__id__), str(mock_node2.__id__), "END"]
        actual_enum = result.custom_parameters["json_schema"]["schema"]["properties"]["next_step"]["enum"]

        assert set(actual_enum) == set(expected_enum)

    def test_process_parameters_without_custom_parameters(self):
        parameters = PromptParameters()

        class TestPromptNode(BaseInlinePromptNode):
            ml_model = "test-model"
            blocks = []

        node = TestPromptNode()
        node.parameters = parameters

        result = node._process_parameters_for_dynamic_schema()

        assert result == parameters

    def test_process_parameters_without_json_schema(self):
        custom_parameters = {"temperature": 0.8}
        parameters = PromptParameters(custom_parameters=custom_parameters)

        class TestPromptNode(BaseInlinePromptNode):
            ml_model = "test-model"
            blocks = []

        node = TestPromptNode()
        node.parameters = parameters

        result = node._process_parameters_for_dynamic_schema()

        assert result == parameters

    def test_process_parameters_without_workflow_nodes(self):
        state = BaseState()
        state.meta = StateMeta()

        custom_parameters = {
            "json_schema": {
                "schema": {"type": "object", "properties": {"action": {"type": "string", "enum": ["$WORKFLOW_NODES"]}}}
            }
        }

        parameters = PromptParameters(custom_parameters=custom_parameters)

        class TestPromptNode(BaseInlinePromptNode):
            ml_model = "test-model"
            blocks = []

        node = TestPromptNode()
        node.state = state
        node.parameters = parameters

        result = node._process_parameters_for_dynamic_schema()

        assert result == parameters

    def test_process_parameters_excludes_current_node(self):
        current_node_id = uuid4()
        mock_node1 = Mock()
        mock_node1.__id__ = current_node_id
        mock_node2 = Mock()
        mock_node2.__id__ = uuid4()

        mock_workflow = Mock()
        mock_workflow.get_nodes.return_value = [mock_node1, mock_node2]

        state = BaseState()
        state.meta = StateMeta(workflow_definition=mock_workflow)

        custom_parameters = {
            "json_schema": {
                "schema": {"type": "object", "properties": {"next": {"type": "string", "enum": ["$WORKFLOW_NODES"]}}}
            }
        }

        parameters = PromptParameters(custom_parameters=custom_parameters)

        class TestPromptNode(BaseInlinePromptNode):
            ml_model = "test-model"
            blocks = []

        node = TestPromptNode()
        node.state = state
        node.__id__ = current_node_id
        node.parameters = parameters

        result = node._process_parameters_for_dynamic_schema()

        actual_enum = result.custom_parameters["json_schema"]["schema"]["properties"]["next"]["enum"]
        assert actual_enum == [str(mock_node2.__id__)]
        assert str(current_node_id) not in actual_enum

    @patch("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.replace")
    def test_process_parameters_creates_new_instance_when_changed(self, mock_replace):
        mock_node1 = Mock()
        mock_node1.__id__ = uuid4()
        current_node_id = uuid4()

        mock_workflow = Mock()
        mock_workflow.get_nodes.return_value = [mock_node1]

        state = BaseState()
        state.meta = StateMeta(workflow_definition=mock_workflow)

        custom_parameters = {
            "json_schema": {
                "schema": {"type": "object", "properties": {"next": {"type": "string", "enum": ["$WORKFLOW_NODES"]}}}
            }
        }

        parameters = PromptParameters(custom_parameters=custom_parameters)
        new_parameters = PromptParameters(custom_parameters={"processed": True})
        mock_replace.return_value = new_parameters

        class TestPromptNode(BaseInlinePromptNode):
            ml_model = "test-model"
            blocks = []

        node = TestPromptNode()
        node.state = state
        node.__id__ = current_node_id
        node.parameters = parameters

        result = node._process_parameters_for_dynamic_schema()

        mock_replace.assert_called_once()
        assert result == new_parameters
