from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_workflow_serialization__dependencies_from_ml_models():
    """
    Tests that model provider dependencies are extracted from prompt nodes
    when ml_models list is provided during workflow serialization via serialize_module.
    """

    # GIVEN a workflow module with a prompt node that uses gpt-4o-mini
    module = "ee.codegen_integration.fixtures.simple_prompt_node.code"

    # AND a list of ML models as raw dicts (as the client would provide)
    ml_models = [
        {"name": "gpt-4o-mini", "hosted_by": "OPENAI"},
        {"name": "claude-3-opus", "hosted_by": "ANTHROPIC"},
    ]

    # WHEN we serialize the module with ml_models provided
    result = BaseWorkflowDisplay.serialize_module(module, ml_models=ml_models)

    # THEN we should get the expected dependency for the model used in the workflow
    dependencies = result.exec_config.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "MODEL_PROVIDER",
        "name": "OPENAI",
        "model_name": "gpt-4o-mini",
    }
