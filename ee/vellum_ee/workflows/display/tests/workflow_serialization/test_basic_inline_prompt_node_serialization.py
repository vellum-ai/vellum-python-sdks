from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_inline_prompt_node_with_functions.workflow import BasicInlinePromptWithFunctionsWorkflow


def test_serialize_workflow():
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicInlinePromptWithFunctionsWorkflow
    )
    serialized_workflow: dict = workflow_display.serialize()
    assert (
        serialized_workflow["workflow_raw_data"]["nodes"][-2]["data"]["exec_config"]["prompt_template_block_data"][
            "blocks"
        ][-1]["block_type"]
        == "FUNCTION_DEFINITION"
    )
