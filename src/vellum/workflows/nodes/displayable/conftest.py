import pytest
from uuid import UUID

from vellum.workflows.events.types import (
    CodeResourceDefinition,
    NodeParentContext,
    WorkflowDeploymentParentContext,
    WorkflowParentContext,
)


@pytest.fixture
def mock_complex_parent_context():
    # TODO: We were able to confirm that this parent context caused our serialization to hang, but don't know why yet.
    # We should try to reduce this example further to isolate a minimal example that reproduces the issue.
    return NodeParentContext(
        span_id=UUID("d697f8c8-b363-4154-8469-eb4f9fb5e445"),
        parent=WorkflowParentContext(
            span_id=UUID("a0c68884-22c3-4ac9-8476-8747884d80e1"),
            parent=NodeParentContext(
                span_id=UUID("46163407-71f7-40f2-9f66-872d4b338fcc"),
                parent=WorkflowParentContext(
                    span_id=UUID("0ddf01e7-d0c3-426c-af27-d8bfb22fcdd5"),
                    parent=NodeParentContext(
                        span_id=UUID("79a6c926-b5f3-4ede-b2f8-4bb6f0c086ba"),
                        parent=WorkflowParentContext(
                            span_id=UUID("530a56fe-90fd-4f4c-b905-457975fb3e10"),
                            parent=WorkflowDeploymentParentContext(
                                span_id=UUID("3e10a8c2-558c-4ef7-926d-7b79ebc7cba9"),
                                parent=NodeParentContext(
                                    span_id=UUID("a3cd4086-c0b9-4dff-88f3-3e2191b8a2a7"),
                                    parent=WorkflowParentContext(
                                        span_id=UUID("c2ba7577-8d24-49b1-aa92-b9ace8244090"),
                                        workflow_definition=CodeResourceDefinition(
                                            id=UUID("2e2d5c56-49b7-48b5-82fa-e80e72768b9c"),
                                            name="Workflow",
                                            module=["e81a6124-2c57-4c39-938c-ab6059059ff2", "workflow"],
                                        ),
                                    ),
                                    node_definition=CodeResourceDefinition(
                                        id=UUID("23d25675-f377-4450-916f-39ebee5c8ea9"),
                                        name="SubworkflowDeployment",
                                        module=[
                                            "e81a6124-2c57-4c39-938c-ab6059059ff2",
                                            "nodes",
                                            "subworkflow_deployment",
                                        ],
                                    ),
                                ),
                                deployment_id=UUID("cfc99610-2869-4506-b106-3fd7ce0bbb15"),
                                deployment_name="my-deployment",
                                deployment_history_item_id=UUID("13f31aae-29fd-4066-a4ec-c7687faebae3"),
                                release_tag_id=UUID("2d03987a-dcb5-49b9-981e-5e871c8f5d97"),
                                release_tag_name="LATEST",
                                external_id=None,
                                metadata=None,
                                workflow_version_id=UUID("7eaae816-b5f3-436d-8597-e8c3e4a32958"),
                            ),
                            workflow_definition=CodeResourceDefinition(
                                id=UUID("2e2d5c56-49b7-48b5-82fa-e80e72768b9c"),
                                name="Workflow",
                                module=["3e10a8c2-558c-4ef7-926d-7b79ebc7cba9", "workflow"],
                            ),
                        ),
                        node_definition=CodeResourceDefinition(
                            id=UUID("42c8adc2-a0d6-499e-81a4-e2e02d7beba9"),
                            name="MyNode",
                            module=[
                                "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                                "nodes",
                                "my_node",
                            ],
                        ),
                    ),
                    workflow_definition=CodeResourceDefinition(
                        id=UUID("b8563da0-7fd4-42e0-a75e-9ef037fca5a1"),
                        name="MyNodeWorkflow",
                        module=[
                            "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                            "nodes",
                            "my_node",
                            "workflow",
                        ],
                    ),
                ),
                node_definition=CodeResourceDefinition(
                    id=UUID("d44aee53-3b6e-41fd-8b7a-908cb2c77821"),
                    name="RetryNode",
                    module=[
                        "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                        "nodes",
                        "my_node",
                        "nodes",
                        "my_prompt",
                        "MyPrompt",
                        "<adornment>",
                    ],
                ),
            ),
            workflow_definition=CodeResourceDefinition(
                id=UUID("568a28dd-7134-436e-a5f4-790675212b51"),
                name="Subworkflow",
                module=["vellum", "workflows", "nodes", "utils"],
            ),
        ),
        node_definition=CodeResourceDefinition(
            id=UUID("86a34e5c-2652-49f0-9f9e-c653cf70029a"),
            name="MyPrompt",
            module=[
                "3e10a8c2-558c-4ef7-926d-7b79ebc7cba9",
                "nodes",
                "my_node",
                "nodes",
                "my_prompt",
            ],
        ),
    )
