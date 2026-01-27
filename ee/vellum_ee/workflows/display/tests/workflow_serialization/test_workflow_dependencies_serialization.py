from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.utils.dependencies import MLModel, MLModelHostingInterface
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_workflow_serialization__dependencies_from_ml_models():
    """
    Tests that model provider dependencies are extracted from prompt nodes
    when ml_models list is provided during workflow serialization.
    """

    # GIVEN a workflow with a prompt node that uses a specific model
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

    # AND a list of ML models that the client provides
    ml_models = [
        MLModel(name="gpt-4o", hosted_by=MLModelHostingInterface.OPENAI),
        MLModel(name="claude-3-opus", hosted_by=MLModelHostingInterface.ANTHROPIC),
    ]

    # WHEN we serialize the workflow with ml_models provided
    workflow_display = get_workflow_display(workflow_class=TestWorkflow, ml_models=ml_models)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get the expected dependency for the model used in the workflow
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "MODEL_PROVIDER",
        "name": "OPENAI",
        "model_name": "gpt-4o",
    }
