from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.utils.uuids import uuid4_from_hash


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

    expected_hash = str(uuid4_from_hash(f"{deployment_name}_{release_tag}"))
    expected_prefix = f"vellum_workflow_deployment_{expected_hash}"

    # Create a simple test node for the resolved workflow
    test_node_code = """
from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.outputs import BaseOutputs

class TestNode(TemplatingNode):
    template = "Hello World"

    class Outputs(BaseOutputs):
        result: str
"""

    mock_workflow_code = """
from vellum.workflows import BaseWorkflow
from .nodes.test_node import TestNode

class ResolvedWorkflow(BaseWorkflow):
    graph = TestNode
"""
    # Create parent workflow files that reference the subworkflow deployment
    parent_workflow_code = """
from vellum.workflows import BaseWorkflow
from .nodes.subworkflow_deployment_node import TestSubworkflowDeploymentNode

class ParentWorkflow(BaseWorkflow):
    graph = TestSubworkflowDeploymentNode
"""

    parent_node_code = """
from vellum.workflows.nodes import SubworkflowDeploymentNode
from vellum.workflows.outputs import BaseOutputs

class TestSubworkflowDeploymentNode(SubworkflowDeploymentNode):
    deployment = "test_deployment"

    class Outputs(BaseOutputs):
        result: str

    subworkflow_inputs = {"message": "test"}
"""

    generated_files = {
        f"{expected_prefix}/workflow.py": mock_workflow_code,
        f"{expected_prefix}/nodes/test_node.py": test_node_code,
        "workflow.py": parent_workflow_code,
        "nodes/subworkflow_deployment_node.py": parent_node_code,
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
