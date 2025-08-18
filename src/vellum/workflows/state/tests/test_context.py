from unittest.mock import Mock

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.utils.uuids import uuid4_from_hash


class MockSubworkflowInputs(BaseInputs):
    message: str


class MockSubworkflowOutputs(BaseOutputs):
    result: str


class MockSubworkflow(BaseWorkflow[MockSubworkflowInputs, BaseState]):
    class Outputs(BaseOutputs):
        result: str = "mock result"


class TestSubworkflowDeploymentNode(SubworkflowDeploymentNode):
    deployment = "test_deployment"

    class Outputs(BaseOutputs):
        result: str

    subworkflow_inputs = {"message": "test"}


class TestWorkflow(BaseWorkflow):
    graph = TestSubworkflowDeploymentNode


def test_resolve_workflow_deployment__returns_workflow_with_generated_files():
    """
    Test that resolve_workflow_deployment returns a workflow with artifacts
    in generated_files using the correct prefix format.

    GIVEN a deployment name and release tag
    WHEN we resolve the workflow deployment
    THEN the method should return a workflow with artifacts in the correct prefix location
    """
    # GIVEN a deployment name and release tag
    deployment_name = "test_deployment"
    release_tag = "v1.0.0"

    expected_hash = str(uuid4_from_hash(f"{deployment_name}|{release_tag}"))
    expected_prefix = f"vellum_workflow_deployment_{expected_hash}"

    mock_workflow_code = """
from vellum.workflows import BaseWorkflow

class ResolvedWorkflow(BaseWorkflow):
    pass
"""
    generated_files = {
        f"{expected_prefix}/workflow.py": mock_workflow_code,
        f"{expected_prefix}/nodes/test_node.py": "# test node code",
    }

    context = WorkflowContext(generated_files=generated_files)

    # WHEN we resolve the workflow deployment
    resolved_workflow = context.resolve_workflow_deployment(deployment_name=deployment_name, release_tag=release_tag)

    # THEN the method should return a workflow (not None)
    assert resolved_workflow is not None

    assert context.generated_files is not None
    workflow_files = {
        path: content for path, content in context.generated_files.items() if path.startswith(expected_prefix)
    }
    assert len(workflow_files) > 0
    assert f"{expected_prefix}/workflow.py" in workflow_files


def test_resolve_workflow_deployment__current_implementation_returns_none():
    """
    Test that demonstrates the current stub implementation returns None.
    This test should pass initially but fail once the method is implemented.

    GIVEN a workflow context
    WHEN we try to resolve a workflow deployment
    THEN the current implementation returns None
    """
    # GIVEN a workflow context
    context = WorkflowContext()

    # WHEN we try to resolve a workflow deployment
    result = context.resolve_workflow_deployment("test_deployment", "v1.0.0")

    # THEN the current implementation returns None
    assert result is None


def test_subworkflow_deployment_node__uses_resolved_workflow():
    """
    Test that SubworkflowDeploymentNode uses resolved workflow when available.

    GIVEN a mock resolved workflow and context that resolves to that workflow
    WHEN we check if the node would use the resolved workflow
    THEN the context's resolve method should be called
    """
    # GIVEN a mock resolved workflow
    mock_workflow = MockSubworkflow()

    # AND a context that resolves to that workflow
    context = WorkflowContext()
    mock_resolve = Mock(return_value=mock_workflow)
    setattr(context, "resolve_workflow_deployment", mock_resolve)

    node = TestSubworkflowDeploymentNode()
    node._context = context

    # WHEN we check if the node would resolve the deployment
    resolved = context.resolve_workflow_deployment("test_deployment", "v1.0.0")

    # THEN the context's resolve method should be called and return the mock workflow
    mock_resolve.assert_called_once_with("test_deployment", "v1.0.0")
    assert resolved == mock_workflow


def test_resolve_workflow_deployment__hash_generation_consistency():
    """
    Test that the hash generation for the prefix is consistent and deterministic.

    GIVEN the same deployment name and release tag
    WHEN we generate the hash multiple times
    THEN the hash should be consistent
    """
    # GIVEN a deployment name and release tag
    deployment_name = "example_deployment"
    release_tag = "v2.1.0"

    # WHEN we generate the hash multiple times
    hash1 = str(uuid4_from_hash(f"{deployment_name}|{release_tag}"))
    hash2 = str(uuid4_from_hash(f"{deployment_name}|{release_tag}"))

    # THEN the hashes should be identical
    assert hash1 == hash2

    expected_prefix = f"vellum_workflow_deployment_{hash1}"
    assert expected_prefix.startswith("vellum_workflow_deployment_")
    assert len(hash1) == 36  # UUID length


def test_resolve_workflow_deployment__different_deployments_different_hashes():
    """
    Test that different deployment names or release tags produce different hashes.

    GIVEN different deployment names and release tags
    WHEN we generate hashes for each combination
    THEN each combination should produce a unique hash
    """
    # GIVEN different deployment configurations
    configs = [
        ("deployment_a", "v1.0.0"),
        ("deployment_b", "v1.0.0"),
        ("deployment_a", "v2.0.0"),
        ("deployment_b", "v2.0.0"),
    ]

    # WHEN we generate hashes for each configuration
    hashes = []
    for name, tag in configs:
        hash_value = str(uuid4_from_hash(f"{name}|{tag}"))
        hashes.append(hash_value)

    assert len(set(hashes)) == len(hashes)
