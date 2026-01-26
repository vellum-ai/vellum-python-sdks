from typing import Any, Dict, List, cast

from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.utils.dependencies import (
    ModelPrefixMapping,
    extract_model_provider_dependencies,
    infer_model_hosting_interface,
)

# Stub mapping for testing- uses fake providers to avoid coupling to real provider names
STUB_PREFIX_MAP: ModelPrefixMapping = {
    "foo-": ("FOO_PROVIDER", "Foo Provider"),
    "bar-": ("BAR_PROVIDER", "Bar Provider"),
    "baz-": ("BAZ_PROVIDER", "Baz Provider"),
}


class TestInferModelHostingInterface:
    """Tests for the infer_model_hosting_interface function."""

    def test_infer_model_hosting_interface__known_prefix(self) -> None:
        """Tests that known model prefixes are correctly mapped to hosting interfaces."""
        # GIVEN a stub prefix mapping
        prefix_map = STUB_PREFIX_MAP

        # WHEN we infer the hosting interface for a model with a known prefix
        result = infer_model_hosting_interface("foo-model-v1", prefix_map)

        # THEN we should get the expected interface and label
        assert result is not None
        assert result[0] == "FOO_PROVIDER"
        assert result[1] == "Foo Provider"

    def test_infer_model_hosting_interface__unknown_model(self) -> None:
        """Tests that unknown models return None."""
        # GIVEN a stub prefix mapping
        prefix_map = STUB_PREFIX_MAP

        # WHEN we infer the hosting interface for an unknown model
        result = infer_model_hosting_interface("unknown-model-xyz", prefix_map)

        # THEN we should get None
        assert result is None

    def test_infer_model_hosting_interface__case_insensitive(self) -> None:
        """Tests that model name matching is case-insensitive."""
        # GIVEN a stub prefix mapping
        prefix_map = STUB_PREFIX_MAP

        # WHEN we infer the hosting interface with different cases
        result_lower = infer_model_hosting_interface("foo-model", prefix_map)
        result_upper = infer_model_hosting_interface("FOO-MODEL", prefix_map)
        result_mixed = infer_model_hosting_interface("FoO-mOdEl", prefix_map)

        # THEN all should return the same result
        assert result_lower == result_upper == result_mixed == ("FOO_PROVIDER", "Foo Provider")

    def test_infer_model_hosting_interface__empty_mapping(self) -> None:
        """Tests that empty mapping returns None for any model."""
        # GIVEN an empty prefix mapping
        prefix_map: ModelPrefixMapping = {}

        # WHEN we infer the hosting interface for any model
        result = infer_model_hosting_interface("foo-model", prefix_map)

        # THEN we should get None
        assert result is None


class TestExtractModelProviderDependencies:
    """Tests for the extract_model_provider_dependencies function."""

    def test_extract_model_provider_dependencies__single_prompt_node(self) -> None:
        """Tests extraction from a single prompt node."""
        # GIVEN a list of serialized nodes with one prompt node
        serialized_nodes: List[JsonObject] = [
            cast(
                JsonObject,
                {
                    "id": "node-1",
                    "type": "PROMPT",
                    "data": cast(JsonObject, {"ml_model_name": "foo-model-v1"}),
                },
            )
        ]

        # WHEN we extract dependencies with a stub mapping
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN we should get one dependency
        assert isinstance(dependencies, list)
        assert len(dependencies) == 1
        dep = dependencies[0]
        assert isinstance(dep, dict)
        assert dep == {
            "type": "MODEL_PROVIDER",
            "name": "FOO_PROVIDER",
            "label": "Foo Provider",
            "model_name": "foo-model-v1",
        }

    def test_extract_model_provider_dependencies__multiple_prompt_nodes_same_model(self) -> None:
        """Tests that duplicate models are deduplicated."""
        # GIVEN multiple prompt nodes with the same model
        serialized_nodes: List[JsonObject] = [
            cast(
                JsonObject,
                {"id": "node-1", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model"})},
            ),
            cast(
                JsonObject,
                {"id": "node-2", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model"})},
            ),
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN we should get only one dependency (deduplicated)
        assert isinstance(dependencies, list)
        assert len(dependencies) == 1

    def test_extract_model_provider_dependencies__multiple_different_models(self) -> None:
        """Tests extraction from multiple prompt nodes with different models."""
        # GIVEN multiple prompt nodes with different models
        serialized_nodes: List[JsonObject] = [
            cast(
                JsonObject,
                {"id": "node-1", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model"})},
            ),
            cast(
                JsonObject,
                {"id": "node-2", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "bar-model"})},
            ),
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN we should get two dependencies
        assert isinstance(dependencies, list)
        assert len(dependencies) == 2
        model_names = {cast(Dict[str, Any], dep)["model_name"] for dep in dependencies}
        assert model_names == {"foo-model", "bar-model"}

    def test_extract_model_provider_dependencies__non_prompt_nodes_ignored(self) -> None:
        """Tests that non-prompt nodes are ignored."""
        # GIVEN a mix of node types
        serialized_nodes: List[JsonObject] = [
            cast(JsonObject, {"id": "node-1", "type": "ENTRYPOINT", "data": cast(JsonObject, {})}),
            cast(
                JsonObject,
                {"id": "node-2", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model"})},
            ),
            cast(JsonObject, {"id": "node-3", "type": "TEMPLATING", "data": cast(JsonObject, {})}),
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN we should only get the prompt node dependency
        assert isinstance(dependencies, list)
        assert len(dependencies) == 1
        dep = dependencies[0]
        assert isinstance(dep, dict)
        assert dep["model_name"] == "foo-model"

    def test_extract_model_provider_dependencies__unknown_model_skipped(self) -> None:
        """Tests that unknown models are skipped."""
        # GIVEN a prompt node with an unknown model
        serialized_nodes: List[JsonObject] = [
            cast(
                JsonObject,
                {"id": "node-1", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "unknown-model"})},
            ),
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN we should get no dependencies
        assert isinstance(dependencies, list)
        assert len(dependencies) == 0

    def test_extract_model_provider_dependencies__empty_list(self) -> None:
        """Tests extraction from an empty list."""
        # WHEN we extract dependencies from an empty list
        dependencies = extract_model_provider_dependencies([], STUB_PREFIX_MAP)

        # THEN we should get an empty list
        assert dependencies == []

    def test_extract_model_provider_dependencies__missing_ml_model_name(self) -> None:
        """Tests that nodes without ml_model_name are skipped."""
        # GIVEN a prompt node without ml_model_name
        serialized_nodes: List[JsonObject] = [
            cast(JsonObject, {"id": "node-1", "type": "PROMPT", "data": cast(JsonObject, {})}),
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN we should get no dependencies
        assert isinstance(dependencies, list)
        assert len(dependencies) == 0

    def test_extract_model_provider_dependencies__case_insensitive_deduplication(self) -> None:
        """Tests that model deduplication is case-insensitive."""
        # GIVEN multiple prompt nodes with the same model in different cases
        serialized_nodes: List[JsonObject] = [
            cast(
                JsonObject,
                {"id": "node-1", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model"})},
            ),
            cast(
                JsonObject,
                {"id": "node-2", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "FOO-MODEL"})},
            ),
            cast(
                JsonObject,
                {"id": "node-3", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "FoO-mOdEl"})},
            ),
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN we should get only one dependency (case-insensitive deduplication)
        assert isinstance(dependencies, list)
        assert len(dependencies) == 1

    def test_extract_model_provider_dependencies__sorted_alphabetically(self) -> None:
        """Tests that dependencies are sorted alphabetically by (name, model_name)."""
        # GIVEN multiple prompt nodes with different models in non-alphabetical order
        serialized_nodes: List[JsonObject] = [
            cast(
                JsonObject,
                {"id": "node-1", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model-2"})},
            ),
            cast(
                JsonObject,
                {"id": "node-2", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "bar-model"})},
            ),
            cast(
                JsonObject,
                {"id": "node-3", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model-1"})},
            ),
        ]

        # WHEN we extract dependencies
        dependencies = extract_model_provider_dependencies(serialized_nodes, STUB_PREFIX_MAP)

        # THEN dependencies should be sorted by (name, model_name)
        assert isinstance(dependencies, list)
        assert len(dependencies) == 3
        dep0 = dependencies[0]
        dep1 = dependencies[1]
        dep2 = dependencies[2]
        assert isinstance(dep0, dict)
        assert isinstance(dep1, dict)
        assert isinstance(dep2, dict)
        # BAR_PROVIDER comes before FOO_PROVIDER alphabetically
        assert dep0["name"] == "BAR_PROVIDER"
        assert dep0["model_name"] == "bar-model"
        # FOO_PROVIDER models sorted by model_name
        assert dep1["name"] == "FOO_PROVIDER"
        assert dep1["model_name"] == "foo-model-1"
        assert dep2["name"] == "FOO_PROVIDER"
        assert dep2["model_name"] == "foo-model-2"

    def test_extract_model_provider_dependencies__empty_mapping(self) -> None:
        """Tests that empty mapping produces no dependencies."""
        # GIVEN a prompt node with a model
        serialized_nodes: List[JsonObject] = [
            cast(
                JsonObject,
                {"id": "node-1", "type": "PROMPT", "data": cast(JsonObject, {"ml_model_name": "foo-model"})},
            ),
        ]

        # WHEN we extract dependencies with an empty mapping
        dependencies = extract_model_provider_dependencies(serialized_nodes, {})

        # THEN we should get no dependencies
        assert isinstance(dependencies, list)
        assert len(dependencies) == 0
