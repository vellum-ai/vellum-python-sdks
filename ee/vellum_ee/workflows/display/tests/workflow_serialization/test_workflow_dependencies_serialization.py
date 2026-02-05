from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from vellum import DeploymentRead, MlModelRead, PromptDeploymentRelease
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.prompt_deployment_release_prompt_deployment import PromptDeploymentReleasePromptDeployment
from vellum.client.types.prompt_deployment_release_prompt_version import PromptDeploymentReleasePromptVersion
from vellum.client.types.release_environment import ReleaseEnvironment as ReleaseEnvironmentType
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.nodes import InlineSubworkflowNode, MapNode, PromptDeploymentNode
from vellum.workflows.nodes.displayable.inline_prompt_node import InlinePromptNode
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import VellumIntegrationToolDefinition
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


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


def test_workflow_serialization__integration_dependencies_from_tool_calling_node():
    """
    Tests that integration dependencies are extracted from tool calling nodes
    that use VellumIntegrationToolDefinition.
    """

    # GIVEN a VellumIntegrationToolDefinition for GitHub
    github_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="GITHUB",
        name="create_issue",
        description="Create a new issue in a GitHub repository",
    )

    # AND a ToolCallingNode that uses this tool
    class TestInputs(BaseInputs):
        query: str

    class TestToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="question"),
                        ],
                    ),
                ],
            ),
        ]
        functions = [github_tool]
        prompt_inputs = {"question": TestInputs.query}

    class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
        graph = TestToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            text = TestToolCallingNode.Outputs.text

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get the expected integration dependency
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "INTEGRATION",
        "provider": "COMPOSIO",
        "name": "GITHUB",
    }


def test_workflow_serialization__multiple_integration_dependencies_deduplicated():
    """
    Tests that multiple tool calling nodes using the same integration
    result in a single deduplicated dependency.
    """

    # GIVEN two VellumIntegrationToolDefinitions for the same integration
    github_tool_1 = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="GITHUB",
        name="create_issue",
        description="Create a new issue",
    )
    github_tool_2 = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="GITHUB",
        name="list_issues",
        description="List issues",
    )

    # AND a ToolCallingNode that uses both tools
    class TestInputs(BaseInputs):
        query: str

    class TestToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="question"),
                        ],
                    ),
                ],
            ),
        ]
        functions = [github_tool_1, github_tool_2]
        prompt_inputs = {"question": TestInputs.query}

    class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
        graph = TestToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            text = TestToolCallingNode.Outputs.text

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get only one integration dependency (deduplicated)
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "INTEGRATION",
        "provider": "COMPOSIO",
        "name": "GITHUB",
    }


def test_workflow_serialization__multiple_different_integration_dependencies():
    """
    Tests that multiple different integration dependencies are all captured.
    """

    # GIVEN VellumIntegrationToolDefinitions for different integrations
    github_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="GITHUB",
        name="create_issue",
        description="Create a GitHub issue",
    )
    slack_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="SLACK",
        name="send_message",
        description="Send a Slack message",
    )
    asana_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="ASANA",
        name="create_task",
        description="Create an Asana task",
    )

    # AND a ToolCallingNode that uses all tools
    class TestInputs(BaseInputs):
        query: str

    class TestToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="question"),
                        ],
                    ),
                ],
            ),
        ]
        functions = [slack_tool, github_tool, asana_tool]
        prompt_inputs = {"question": TestInputs.query}

    class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
        graph = TestToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            text = TestToolCallingNode.Outputs.text

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get all three integration dependencies
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 3

    # AND all expected dependencies should be present (order not guaranteed)
    expected_deps = [
        {"type": "INTEGRATION", "provider": "COMPOSIO", "name": "ASANA"},
        {"type": "INTEGRATION", "provider": "COMPOSIO", "name": "GITHUB"},
        {"type": "INTEGRATION", "provider": "COMPOSIO", "name": "SLACK"},
    ]
    for expected in expected_deps:
        assert expected in dependencies


def test_workflow_serialization__dependencies_from_inline_subworkflow():
    """
    Tests that dependencies are extracted from inline subworkflow nodes
    and included in the parent workflow's dependencies.
    """

    # GIVEN a subworkflow with a prompt node that uses gpt-4o-mini
    class SubworkflowInputs(BaseInputs):
        query: str

    class SubworkflowPromptNode(InlinePromptNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="question"),
                        ],
                    ),
                ],
            ),
        ]
        prompt_inputs = {"question": SubworkflowInputs.query}

    class SubWorkflow(BaseWorkflow[SubworkflowInputs, BaseState]):
        graph = SubworkflowPromptNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowPromptNode.Outputs.text

    # AND a parent workflow with an inline subworkflow node
    class ParentInputs(BaseInputs):
        query: str

    class SubworkflowNode(InlineSubworkflowNode):
        subworkflow = SubWorkflow
        subworkflow_inputs = {"query": ParentInputs.query}

    class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
        graph = SubworkflowNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowNode.Outputs.text

    # WHEN we serialize the parent workflow with ml_models provided
    ml_models = [
        {"name": "gpt-4o-mini", "hosted_by": "OPENAI"},
    ]
    workflow_display = get_workflow_display(workflow_class=ParentWorkflow, ml_models=ml_models)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get the model provider dependency from the subworkflow
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "MODEL_PROVIDER",
        "name": "OPENAI",
        "model_name": "gpt-4o-mini",
    }


def test_workflow_serialization__dependencies_from_inline_subworkflow_with_integration():
    """
    Tests that integration dependencies are extracted from inline subworkflow nodes
    that contain tool calling nodes with integrations.
    """

    # GIVEN a VellumIntegrationToolDefinition for GitHub
    github_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="GITHUB",
        name="create_issue",
        description="Create a new issue in a GitHub repository",
    )

    # AND a subworkflow with a tool calling node that uses this tool
    class SubworkflowInputs(BaseInputs):
        query: str

    class SubworkflowToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="question"),
                        ],
                    ),
                ],
            ),
        ]
        functions = [github_tool]
        prompt_inputs = {"question": SubworkflowInputs.query}

    class SubWorkflow(BaseWorkflow[SubworkflowInputs, BaseState]):
        graph = SubworkflowToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowToolCallingNode.Outputs.text

    # AND a parent workflow with an inline subworkflow node
    class ParentInputs(BaseInputs):
        query: str

    class SubworkflowNode(InlineSubworkflowNode):
        subworkflow = SubWorkflow
        subworkflow_inputs = {"query": ParentInputs.query}

    class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
        graph = SubworkflowNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowNode.Outputs.text

    # WHEN we serialize the parent workflow
    workflow_display = get_workflow_display(workflow_class=ParentWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get the integration dependency from the subworkflow
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "INTEGRATION",
        "provider": "COMPOSIO",
        "name": "GITHUB",
    }


def test_workflow_serialization__dependencies_from_inline_subworkflow_deduplicated():
    """
    Tests that dependencies from inline subworkflows are deduplicated
    when multiple subworkflows use the same dependency.
    """

    # GIVEN a subworkflow with a prompt node that uses gpt-4o-mini
    class SubworkflowInputs(BaseInputs):
        query: str

    class SubworkflowPromptNode(InlinePromptNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="question"),
                        ],
                    ),
                ],
            ),
        ]
        prompt_inputs = {"question": SubworkflowInputs.query}

    class SubWorkflow(BaseWorkflow[SubworkflowInputs, BaseState]):
        graph = SubworkflowPromptNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowPromptNode.Outputs.text

    # AND a parent workflow with two inline subworkflow nodes using the same subworkflow
    class ParentInputs(BaseInputs):
        query: str

    class SubworkflowNode1(InlineSubworkflowNode):
        subworkflow = SubWorkflow
        subworkflow_inputs = {"query": ParentInputs.query}

    class SubworkflowNode2(InlineSubworkflowNode):
        subworkflow = SubWorkflow
        subworkflow_inputs = {"query": ParentInputs.query}

    class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
        graph = SubworkflowNode1 >> SubworkflowNode2

        class Outputs(BaseWorkflow.Outputs):
            text1 = SubworkflowNode1.Outputs.text
            text2 = SubworkflowNode2.Outputs.text

    # WHEN we serialize the parent workflow with ml_models provided
    ml_models = [
        {"name": "gpt-4o-mini", "hosted_by": "OPENAI"},
    ]
    workflow_display = get_workflow_display(workflow_class=ParentWorkflow, ml_models=ml_models)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get only one model provider dependency (deduplicated)
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "MODEL_PROVIDER",
        "name": "OPENAI",
        "model_name": "gpt-4o-mini",
    }


def test_workflow_serialization__dependencies_from_map_node():
    """
    Tests that dependencies are extracted from map node subworkflows
    and included in the parent workflow's dependencies.
    """

    # GIVEN a subworkflow with a prompt node that uses gpt-4o-mini
    class SubworkflowPromptNode(InlinePromptNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="item"),
                        ],
                    ),
                ],
            ),
        ]
        prompt_inputs = {"item": MapNode.SubworkflowInputs.item}

    class MapSubWorkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = SubworkflowPromptNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowPromptNode.Outputs.text

    # AND a parent workflow with a map node
    class ParentInputs(BaseInputs):
        items: list

    class MapNodeWithDependency(MapNode):
        items = ParentInputs.items
        subworkflow = MapSubWorkflow

    class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
        graph = MapNodeWithDependency

        class Outputs(BaseWorkflow.Outputs):
            text = MapNodeWithDependency.Outputs.text

    # WHEN we serialize the parent workflow with ml_models provided
    ml_models = [
        {"name": "gpt-4o-mini", "hosted_by": "OPENAI"},
    ]
    workflow_display = get_workflow_display(workflow_class=ParentWorkflow, ml_models=ml_models)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get the model provider dependency from the map node's subworkflow
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "MODEL_PROVIDER",
        "name": "OPENAI",
        "model_name": "gpt-4o-mini",
    }


def test_workflow_serialization__dependencies_from_map_node_with_integration():
    """
    Tests that integration dependencies are extracted from map node subworkflows
    that contain tool calling nodes with integrations.
    """

    # GIVEN a VellumIntegrationToolDefinition for GitHub
    github_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="GITHUB",
        name="create_issue",
        description="Create a new issue in a GitHub repository",
    )

    # AND a subworkflow with a tool calling node that uses this tool
    class SubworkflowToolCallingNode(ToolCallingNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="question"),
                        ],
                    ),
                ],
            ),
        ]
        functions = [github_tool]
        prompt_inputs = {"question": MapNode.SubworkflowInputs.item}

    class MapSubWorkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = SubworkflowToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowToolCallingNode.Outputs.text

    # AND a parent workflow with a map node
    class ParentInputs(BaseInputs):
        items: list

    class MapNodeWithIntegration(MapNode):
        items = ParentInputs.items
        subworkflow = MapSubWorkflow

    class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
        graph = MapNodeWithIntegration

        class Outputs(BaseWorkflow.Outputs):
            text = MapNodeWithIntegration.Outputs.text

    # WHEN we serialize the parent workflow
    workflow_display = get_workflow_display(workflow_class=ParentWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get the integration dependency from the map node's subworkflow
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "INTEGRATION",
        "provider": "COMPOSIO",
        "name": "GITHUB",
    }


def test_workflow_serialization__dependencies_from_map_node_deduplicated():
    """
    Tests that dependencies from map node subworkflows are deduplicated
    when multiple map nodes use the same subworkflow.
    """

    # GIVEN a subworkflow with a prompt node that uses gpt-4o-mini
    class SubworkflowPromptNode(InlinePromptNode):
        ml_model = "gpt-4o-mini"
        blocks = [
            ChatMessagePromptBlock(
                chat_role="USER",
                blocks=[
                    RichTextPromptBlock(
                        blocks=[
                            VariablePromptBlock(input_variable="item"),
                        ],
                    ),
                ],
            ),
        ]
        prompt_inputs = {"item": MapNode.SubworkflowInputs.item}

    class MapSubWorkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
        graph = SubworkflowPromptNode

        class Outputs(BaseWorkflow.Outputs):
            text = SubworkflowPromptNode.Outputs.text

    # AND a parent workflow with two map nodes using the same subworkflow
    class ParentInputs(BaseInputs):
        items1: list
        items2: list

    class MapNode1(MapNode):
        items = ParentInputs.items1
        subworkflow = MapSubWorkflow

    class MapNode2(MapNode):
        items = ParentInputs.items2
        subworkflow = MapSubWorkflow

    class ParentWorkflow(BaseWorkflow[ParentInputs, BaseState]):
        graph = MapNode1 >> MapNode2

        class Outputs(BaseWorkflow.Outputs):
            text1 = MapNode1.Outputs.text
            text2 = MapNode2.Outputs.text

    # WHEN we serialize the parent workflow with ml_models provided
    ml_models = [
        {"name": "gpt-4o-mini", "hosted_by": "OPENAI"},
    ]
    workflow_display = get_workflow_display(workflow_class=ParentWorkflow, ml_models=ml_models)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get only one model provider dependency (deduplicated)
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "MODEL_PROVIDER",
        "name": "OPENAI",
        "model_name": "gpt-4o-mini",
    }


def test_workflow_serialization__dependencies_from_prompt_deployment_node():
    """
    Tests that model provider dependencies are extracted from prompt deployment nodes
    when the prompt version has ml_model_to_workspace_id and ml_models are provided.
    """

    # GIVEN a prompt deployment node
    class TestInputs(BaseInputs):
        query: str

    class TestPromptDeploymentNode(PromptDeploymentNode):
        deployment = "test_prompt_deployment"
        prompt_inputs = {"query": TestInputs.query}
        ml_model_fallbacks = ["gpt-4o-mini", "claude-3-opus"]

    class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
        graph = TestPromptDeploymentNode

        class Outputs(BaseWorkflow.Outputs):
            text = TestPromptDeploymentNode.Outputs.text

    # AND mock the deployment retrieval
    deployment = DeploymentRead(
        id=str(uuid4()),
        created=datetime.now(),
        label="Test Prompt Deployment",
        name="test_prompt_deployment",
        last_deployed_on=datetime.now(),
        input_variables=[],
        active_model_version_ids=[],
        last_deployed_history_item_id=str(uuid4()),
    )

    # AND mock the prompt deployment release with ml_model_to_workspace_id
    ml_model_to_workspace_id = str(uuid4())
    prompt_version = PromptDeploymentReleasePromptVersion.model_validate(
        {
            "id": str(uuid4()),
            "build_config": {
                "source": "SANDBOX",
                "sandbox_id": str(uuid4()),
                "sandbox_snapshot_id": str(uuid4()),
                "prompt_id": str(uuid4()),
            },
            "ml_model_to_workspace_id": ml_model_to_workspace_id,
        }
    )

    deployment_release = PromptDeploymentRelease(
        id=str(uuid4()),
        created=datetime.now(),
        environment=ReleaseEnvironmentType(id=str(uuid4()), name="DEVELOPMENT", label="Development"),
        prompt_version=prompt_version,
        deployment=PromptDeploymentReleasePromptDeployment(
            id=deployment.id,
            name="test_prompt_deployment",
        ),
        release_tags=[],
        reviews=[],
    )

    ml_model = MlModelRead(
        id=str(uuid4()),
        name="gpt-4o-mini",
        hosted_by="OPENAI",
        introduced_on=datetime.now(),
    )

    mock_client = MagicMock()
    mock_client.deployments.retrieve.return_value = deployment
    mock_client.deployments.retrieve_prompt_deployment_release.return_value = deployment_release
    mock_client.ml_models.retrieve.return_value = ml_model

    # AND provide ml_models for dependency extraction
    ml_models = [
        {"name": "gpt-4o-mini", "hosted_by": "OPENAI"},
    ]

    # WHEN we serialize the workflow with ml_models provided
    workflow_display = get_workflow_display(workflow_class=TestWorkflow, client=mock_client, ml_models=ml_models)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get the model provider dependency from the prompt deployment
    dependencies = serialized_workflow.get("dependencies", [])
    assert len(dependencies) == 1
    assert dependencies[0] == {
        "type": "MODEL_PROVIDER",
        "name": "OPENAI",
        "model_name": "gpt-4o-mini",
    }

    # AND the ml_models.retrieve should have been called with ml_model_to_workspace_id
    mock_client.ml_models.retrieve.assert_called_once_with(id=ml_model_to_workspace_id)
