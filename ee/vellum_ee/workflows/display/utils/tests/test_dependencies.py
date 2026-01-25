import pytest

from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.utils.dependencies import (
    extract_model_provider_dependencies,
    infer_model_hosting_interface,
)
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class TestInferModelHostingInterface:
    """Tests for the infer_model_hosting_interface function."""

    @pytest.mark.parametrize(
        "model_name,expected_interface,expected_label",
        [
            ("gpt-4o", "OPENAI", "OpenAI"),
            ("gpt-4o-mini", "OPENAI", "OpenAI"),
            ("gpt-3.5-turbo", "OPENAI", "OpenAI"),
            ("o1-preview", "OPENAI", "OpenAI"),
            ("o3-mini", "OPENAI", "OpenAI"),
            ("claude-3-opus", "ANTHROPIC", "Anthropic"),
            ("claude-3-sonnet", "ANTHROPIC", "Anthropic"),
            ("claude-2.1", "ANTHROPIC", "Anthropic"),
            ("gemini-1.5-pro", "GOOGLE", "Google"),
            ("gemini-2.0-flash", "GOOGLE", "Google"),
            ("mistral-large", "MISTRAL_AI", "Mistral AI"),
            ("mixtral-8x7b", "MISTRAL_AI", "Mistral AI"),
            ("deepseek-chat", "DEEP_SEEK", "DeepSeek"),
            ("grok-2", "X_AI", "xAI"),
            ("llama-3.1-70b", "META", "Meta"),
            ("command-r-plus", "COHERE", "Cohere"),
        ],
    )
    def test_infer_model_hosting_interface__known_models(
        self, model_name: str, expected_interface: str, expected_label: str
    ):
        """Tests that known model prefixes are correctly mapped to hosting interfaces."""
        # WHEN we infer the hosting interface for a known model
        result = infer_model_hosting_interface(model_name)

        # THEN we should get the expected interface and label
        assert result is not None
        assert result[0] == expected_interface
        assert result[1] == expected_label

    def test_infer_model_hosting_interface__unknown_model(self):
        """Tests that unknown models return None."""
        # WHEN we infer the hosting interface for an unknown model
        result = infer_model_hosting_interface("unknown-model-xyz")

        # THEN we should get None
        assert result is None

    def test_infer_model_hosting_interface__case_insensitive(self):
        """Tests that model name matching is case-insensitive."""
        # WHEN we infer the hosting interface with different cases
        result_lower = infer_model_hosting_interface("gpt-4o")
        result_upper = infer_model_hosting_interface("GPT-4O")
        result_mixed = infer_model_hosting_interface("GpT-4o")

        # THEN all should return the same result
        assert result_lower == result_upper == result_mixed == ("OPENAI", "OpenAI")


class TestExtractModelProviderDependencies:
    """Tests for the extract_model_provider_dependencies function."""

    def test_extract_model_provider_dependencies__single_prompt_node(self):
        """Tests extraction from a single prompt node."""
        # GIVEN a list of serialized nodes with one prompt node
        serialized_nodes = [
            {
                "id": "node-1",
                "type": "PROMPT",
                "data": {"ml_model_name": "gpt-4o"},
            }
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes)

        # THEN we should get one dependency
        assert len(dependencies) == 1
        assert dependencies[0] == {
            "type": "MODEL_PROVIDER",
            "name": "OPENAI",
            "label": "OpenAI",
            "model_name": "gpt-4o",
        }

    def test_extract_model_provider_dependencies__multiple_prompt_nodes_same_model(self):
        """Tests that duplicate models are deduplicated."""
        # GIVEN multiple prompt nodes with the same model
        serialized_nodes = [
            {"id": "node-1", "type": "PROMPT", "data": {"ml_model_name": "gpt-4o"}},
            {"id": "node-2", "type": "PROMPT", "data": {"ml_model_name": "gpt-4o"}},
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes)

        # THEN we should get only one dependency (deduplicated)
        assert len(dependencies) == 1

    def test_extract_model_provider_dependencies__multiple_different_models(self):
        """Tests extraction from multiple prompt nodes with different models."""
        # GIVEN multiple prompt nodes with different models
        serialized_nodes = [
            {"id": "node-1", "type": "PROMPT", "data": {"ml_model_name": "gpt-4o"}},
            {"id": "node-2", "type": "PROMPT", "data": {"ml_model_name": "claude-3-opus"}},
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes)

        # THEN we should get two dependencies
        assert len(dependencies) == 2
        model_names = {dep["model_name"] for dep in dependencies}
        assert model_names == {"gpt-4o", "claude-3-opus"}

    def test_extract_model_provider_dependencies__non_prompt_nodes_ignored(self):
        """Tests that non-prompt nodes are ignored."""
        # GIVEN a mix of node types
        serialized_nodes = [
            {"id": "node-1", "type": "ENTRYPOINT", "data": {}},
            {"id": "node-2", "type": "PROMPT", "data": {"ml_model_name": "gpt-4o"}},
            {"id": "node-3", "type": "TEMPLATING", "data": {}},
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes)

        # THEN we should only get the prompt node dependency
        assert len(dependencies) == 1
        assert dependencies[0]["model_name"] == "gpt-4o"

    def test_extract_model_provider_dependencies__unknown_model_skipped(self):
        """Tests that unknown models are skipped."""
        # GIVEN a prompt node with an unknown model
        serialized_nodes = [
            {"id": "node-1", "type": "PROMPT", "data": {"ml_model_name": "unknown-model"}},
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes)

        # THEN we should get no dependencies
        assert len(dependencies) == 0

    def test_extract_model_provider_dependencies__empty_list(self):
        """Tests extraction from an empty list."""
        # WHEN we extract dependencies from an empty list
        dependencies = extract_model_provider_dependencies([])

        # THEN we should get an empty list
        assert dependencies == []

    def test_extract_model_provider_dependencies__missing_ml_model_name(self):
        """Tests that nodes without ml_model_name are skipped."""
        # GIVEN a prompt node without ml_model_name
        serialized_nodes = [
            {"id": "node-1", "type": "PROMPT", "data": {}},
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes)

        # THEN we should get no dependencies
        assert len(dependencies) == 0


class TestWorkflowSerializationWithDependencies:
    """Tests for workflow serialization including dependencies."""

    def test_serialize_workflow__includes_dependencies(self):
        """Tests that workflow serialization includes dependencies from prompt nodes."""

        # GIVEN a workflow with an inline prompt node
        class TestInputs(BaseInputs):
            query: str

        class TestPromptNode(InlinePromptNode):
            ml_model = "gpt-4o"
            blocks = [
                ChatMessagePromptBlock(
                    chat_role="SYSTEM",
                    blocks=[JinjaPromptBlock(template="Answer: {{query}}")],
                ),
            ]
            prompt_inputs = {"query": TestInputs.query}

        class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
            graph = TestPromptNode

            class Outputs(BaseWorkflow.Outputs):
                result = TestPromptNode.Outputs.text

        # WHEN we serialize the workflow
        workflow_display = get_workflow_display(workflow_class=TestWorkflow)
        serialized = workflow_display.serialize()

        # THEN the serialized workflow should include dependencies
        assert "dependencies" in serialized
        dependencies = serialized["dependencies"]
        assert len(dependencies) == 1
        assert dependencies[0] == {
            "type": "MODEL_PROVIDER",
            "name": "OPENAI",
            "label": "OpenAI",
            "model_name": "gpt-4o",
        }

    def test_serialize_workflow__multiple_prompt_nodes_different_models(self):
        """Tests that multiple prompt nodes with different models produce multiple dependencies."""

        # GIVEN a workflow with multiple prompt nodes using different models
        class TestInputs(BaseInputs):
            query: str

        class OpenAIPromptNode(InlinePromptNode):
            ml_model = "gpt-4o"
            blocks = [
                ChatMessagePromptBlock(
                    chat_role="SYSTEM",
                    blocks=[JinjaPromptBlock(template="OpenAI: {{query}}")],
                ),
            ]
            prompt_inputs = {"query": TestInputs.query}

        class AnthropicPromptNode(InlinePromptNode):
            ml_model = "claude-3-opus"
            blocks = [
                ChatMessagePromptBlock(
                    chat_role="SYSTEM",
                    blocks=[JinjaPromptBlock(template="Anthropic: {{query}}")],
                ),
            ]
            prompt_inputs = {"query": OpenAIPromptNode.Outputs.text}

        class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
            graph = OpenAIPromptNode >> AnthropicPromptNode

            class Outputs(BaseWorkflow.Outputs):
                result = AnthropicPromptNode.Outputs.text

        # WHEN we serialize the workflow
        workflow_display = get_workflow_display(workflow_class=TestWorkflow)
        serialized = workflow_display.serialize()

        # THEN the serialized workflow should include both dependencies
        assert "dependencies" in serialized
        dependencies = serialized["dependencies"]
        assert len(dependencies) == 2
        model_names = {dep["model_name"] for dep in dependencies}
        assert model_names == {"gpt-4o", "claude-3-opus"}

    def test_serialize_workflow__no_prompt_nodes_no_dependencies(self):
        """Tests that workflows without prompt nodes don't include dependencies key."""

        # GIVEN a workflow without prompt nodes
        class TestInputs(BaseInputs):
            query: str

        from vellum.workflows.nodes import TemplatingNode

        class TestTemplatingNode(TemplatingNode):
            template = "Hello {{query}}"
            inputs = {"query": TestInputs.query}

        class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
            graph = TestTemplatingNode

            class Outputs(BaseWorkflow.Outputs):
                result = TestTemplatingNode.Outputs.result

        # WHEN we serialize the workflow
        workflow_display = get_workflow_display(workflow_class=TestWorkflow)
        serialized = workflow_display.serialize()

        # THEN the serialized workflow should not include dependencies
        assert "dependencies" not in serialized
