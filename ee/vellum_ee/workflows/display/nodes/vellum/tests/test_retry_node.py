from typing import Any, Dict, cast

from vellum.workflows import BaseWorkflow
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


def test_retry_node_parameters():
    """Test that RetryNode parameters are correctly serialized."""

    # GIVEN a RetryNode with specific parameters
    @RetryNode.wrap(max_attempts=5, delay=2.5, retry_on_error_code=WorkflowErrorCode.INVALID_INPUTS)
    class MyRetryNode(BaseNode):
        pass

    # AND a workflow using the node
    class MyWorkflow(BaseWorkflow):
        graph = MyRetryNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(base_display_class=VellumWorkflowDisplay, workflow_class=MyWorkflow)
    serialized_workflow = cast(Dict[str, Any], workflow_display.serialize())

    # THEN the correct inputs should be serialized on the node
    serialized_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] != "ENTRYPOINT"
    )

    retry_adornment = next(
        adornment for adornment in serialized_node["adornments"] if adornment["label"] == "RetryNode"
    )

    max_attempts_attribute = next(attr for attr in retry_adornment["attributes"] if attr["name"] == "max_attempts")
    assert max_attempts_attribute["value"]["value"]["value"] == 5

    delay_attribute = next(attr for attr in retry_adornment["attributes"] if attr["name"] == "delay")
    assert delay_attribute["value"]["value"]["value"] == 2.5

    retry_on_error_code_attribute = next(
        attr for attr in retry_adornment["attributes"] if attr["name"] == "retry_on_error_code"
    )

    assert retry_on_error_code_attribute["value"]["value"]["type"] == "STRING"
    assert retry_on_error_code_attribute["value"]["value"]["value"] == "INVALID_INPUTS"
