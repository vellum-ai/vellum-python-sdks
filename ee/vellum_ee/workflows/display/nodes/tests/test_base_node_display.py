import pytest
from uuid import UUID

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


@pytest.fixture
def node_with_implicit_properties():
    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        pass

    expected_id = UUID("ace7f746-4fe6-45c7-8207-fc8a4d0c7f6f")

    return MyNodeDisplay, expected_id


@pytest.fixture
def node_with_explicit_properties():
    explicit_id = UUID("a422f67a-1d37-43f0-bdfc-1e4618c9496d")

    class MyNode(BaseNode):
        pass

    class MyNodeDisplay(BaseNodeDisplay[MyNode]):
        node_id = explicit_id

    return MyNodeDisplay, explicit_id


@pytest.fixture(
    params=[
        "node_with_implicit_properties",
        "node_with_explicit_properties",
    ]
)
def node_info(request):
    return request.getfixturevalue(request.param)


def test_get_id(node_info):
    node_display, expected_id = node_info

    assert node_display().node_id == expected_id
    assert node_display.infer_node_class().__id__ == expected_id


def test_base_node_adornments__happy_path():
    # GIVEN an adornment node
    @RetryNode.wrap(max_attempts=5)
    class StartNode(BaseNode):
        pass

    # AND a workflow that uses the adornment node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=MyWorkflow,
    )
    exec_config = workflow_display.serialize()

    # THEN the workflow display is created successfully
    assert exec_config is not None
