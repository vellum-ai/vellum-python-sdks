from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.vellum.retry_node import BaseRetryNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.try_node import BaseTryNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


class Inputs(BaseInputs):
    input: str


@RetryNode.wrap(max_attempts=3)
class InnerRetryGenericNode(BaseNode):
    input = Inputs.input

    class Outputs(BaseOutputs):
        output: str


@BaseRetryNodeDisplay.wrap(max_attempts=3)
class InnerRetryGenericNodeDisplay(BaseNodeDisplay[InnerRetryGenericNode]):
    pass


def test_serialize_node__retry(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=InnerRetryGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
        global_node_displays={
            InnerRetryGenericNode.__wrapped_node__: InnerRetryGenericNodeDisplay,
        },
    )

    serialized_node["adornments"][0]["attributes"] = sorted(
        serialized_node["adornments"][0]["attributes"], key=lambda x: x["name"]
    )
    assert not DeepDiff(
        {
            "id": "f2a95e79-7d4b-47ad-b986-4f648297ec65",
            "label": "InnerRetryGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "InnerRetryGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_adornments_serialization",
                ],
            },
            "trigger": {"id": "af9ba01c-4cde-4632-9aa1-7673b42e7bd8", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "c2ecc6c0-f353-4495-9b93-a61a47248556", "name": "default", "type": "DEFAULT"}],
            "adornments": [
                {
                    "id": "5be7d260-74f7-4734-b31b-a46a94539586",
                    "label": "RetryNode",
                    "base": {
                        "name": "RetryNode",
                        "module": ["vellum", "workflows", "nodes", "core", "retry_node", "node"],
                    },
                    "attributes": [
                        {
                            "id": "8a07dc58-3fed-41d4-8ca6-31ee0bb86c61",
                            "name": "delay",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                        {
                            "id": "f388e93b-8c68-4f54-8577-bbd0c9091557",
                            "name": "max_attempts",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 3.0}},
                        },
                        {
                            "id": "73a02e62-4535-4e1f-97b5-1264ca8b1d71",
                            "name": "retry_on_condition",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                        {
                            "id": "c91782e3-140f-4938-9c23-d2a7b85dcdd8",
                            "name": "retry_on_error_code",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                    ],
                }
            ],
            "attributes": [
                {
                    "id": "c363daa7-9482-4c0e-aee8-faa080602ee3",
                    "name": "input",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": str(input_id)},
                }
            ],
            "outputs": [
                {"id": "8aaf6cd8-3fa5-4f17-a60f-ec7da5ec6498", "name": "output", "type": "STRING", "value": None}
            ],
        },
        serialized_node,
    )


def test_serialize_node__retry__no_display():  # GIVEN an adornment node
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


@TryNode.wrap()
class InnerTryGenericNode(BaseNode):
    input = Inputs.input

    class Outputs(BaseOutputs):
        output: str


@BaseTryNodeDisplay.wrap()
class InnerTryGenericNodeDisplay(BaseNodeDisplay[InnerTryGenericNode]):
    pass


def test_serialize_node__try(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        base_class=BaseNodeVellumDisplay,
        node_class=InnerTryGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
        global_node_displays={
            InnerTryGenericNode.__wrapped_node__: InnerTryGenericNodeDisplay,
        },
    )

    assert not DeepDiff(
        {
            "id": str(InnerTryGenericNode.__wrapped_node__.__id__),
            "label": "InnerTryGenericNode",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "InnerTryGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_adornments_serialization",
                ],
            },
            "trigger": {"id": "741f7f75-e921-47a9-8c05-9e66640d0866", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "1b8f8ab5-a656-4015-926c-80655bbd9cb8", "name": "default", "type": "DEFAULT"}],
            "adornments": [
                {
                    "id": "3344083c-a32c-4a32-920b-0fb5093448fa",
                    "label": "TryNode",
                    "base": {
                        "name": "TryNode",
                        "module": ["vellum", "workflows", "nodes", "core", "try_node", "node"],
                    },
                    "attributes": [
                        {
                            "id": "ab2fbab0-e2a0-419b-b1ef-ce11ecf11e90",
                            "name": "on_error_code",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        }
                    ],
                }
            ],
            "attributes": [
                {
                    "id": "4d8b4c2c-4f92-4c7a-abf0-b9c88a15a790",
                    "name": "input",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": str(input_id)},
                }
            ],
            "outputs": [
                {"id": "63ba929b-bf79-44ee-bd1f-d259dbe8d48e", "name": "output", "type": "STRING", "value": None}
            ],
        },
        serialized_node,
    )


def test_serialize_node__stacked():
    @TryNode.wrap()
    @RetryNode.wrap(max_attempts=5)
    class InnerStackedGenericNode(BaseNode):
        pass

    # AND a workflow that uses the adornment node
    class StackedWorkflow(BaseWorkflow):
        graph = InnerStackedGenericNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay,
        workflow_class=StackedWorkflow,
    )
    exec_config = workflow_display.serialize()

    # THEN the workflow display is created successfully
    assert not DeepDiff(
        {
            "workflow_raw_data": {
                "nodes": [
                    {
                        "id": "c14c1c9b-a7a4-4d2c-84fb-c940cfb09525",
                        "type": "ENTRYPOINT",
                        "inputs": [],
                        "data": {
                            "label": "Entrypoint Node",
                            "source_handle_id": "51a5eb25-af14-4bee-9ced-d2aa534ea8e9",
                        },
                        "display_data": {"position": {"x": 0.0, "y": 0.0}},
                        "base": None,
                        "definition": None,
                    },
                    {
                        "id": "074833b0-e142-4bbc-8dec-209a35e178a3",
                        "label": "test_serialize_node__stacked.<locals>.InnerStackedGenericNode",
                        "type": "GENERIC",
                        "display_data": {"position": {"x": 0.0, "y": 0.0}},
                        "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
                        "definition": {
                            "name": "InnerStackedGenericNode",
                            "module": [
                                "vellum_ee",
                                "workflows",
                                "display",
                                "tests",
                                "workflow_serialization",
                                "generic_nodes",
                                "test_adornments_serialization",
                            ],
                        },
                        "trigger": {"id": "f206358d-04a5-41c9-beee-0871a074fa48", "merge_behavior": "AWAIT_ATTRIBUTES"},
                        "ports": [{"id": "408cd5fb-3a3e-4eb2-9889-61111bd6a129", "name": "default", "type": "DEFAULT"}],
                        "adornments": [
                            {
                                "id": "5be7d260-74f7-4734-b31b-a46a94539586",
                                "label": "RetryNode",
                                "base": {
                                    "name": "RetryNode",
                                    "module": ["vellum", "workflows", "nodes", "core", "retry_node", "node"],
                                },
                                "attributes": [
                                    {
                                        "id": "c91782e3-140f-4938-9c23-d2a7b85dcdd8",
                                        "name": "retry_on_error_code",
                                        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                                    },
                                    {
                                        "id": "f388e93b-8c68-4f54-8577-bbd0c9091557",
                                        "name": "max_attempts",
                                        "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 5}},
                                    },
                                    {
                                        "id": "8a07dc58-3fed-41d4-8ca6-31ee0bb86c61",
                                        "name": "delay",
                                        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                                    },
                                    {
                                        "id": "73a02e62-4535-4e1f-97b5-1264ca8b1d71",
                                        "name": "retry_on_condition",
                                        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                                    },
                                ],
                            },
                            {
                                "id": "3344083c-a32c-4a32-920b-0fb5093448fa",
                                "label": "TryNode",
                                "base": {
                                    "name": "TryNode",
                                    "module": ["vellum", "workflows", "nodes", "core", "try_node", "node"],
                                },
                                "attributes": [
                                    {
                                        "id": "ab2fbab0-e2a0-419b-b1ef-ce11ecf11e90",
                                        "name": "on_error_code",
                                        "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                                    }
                                ],
                            },
                        ],
                        "attributes": [],
                        "outputs": [],
                    },
                ],
                "edges": [
                    {
                        "id": "e8bd50dd-37a0-49b0-8b7b-f1dd8eb478b9",
                        "source_node_id": "c14c1c9b-a7a4-4d2c-84fb-c940cfb09525",
                        "source_handle_id": "51a5eb25-af14-4bee-9ced-d2aa534ea8e9",
                        "target_node_id": "074833b0-e142-4bbc-8dec-209a35e178a3",
                        "target_handle_id": "f206358d-04a5-41c9-beee-0871a074fa48",
                        "type": "DEFAULT",
                    }
                ],
                "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
                "definition": {
                    "name": "StackedWorkflow",
                    "module": [
                        "vellum_ee",
                        "workflows",
                        "display",
                        "tests",
                        "workflow_serialization",
                        "generic_nodes",
                        "test_adornments_serialization",
                    ],
                },
            },
            "input_variables": [],
            "state_variables": [],
            "output_variables": [],
        },
        exec_config,
        ignore_order=True,
    )
