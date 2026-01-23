from uuid import uuid4
from typing import Any, Dict, List, cast

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import WorkflowInputsDisplay
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.retry_node import BaseRetryNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.try_node import BaseTryNodeDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: str


def test_serialize_node__retry(serialize_node):
    @RetryNode.wrap(max_attempts=3)
    class InnerRetryGenericNode(BaseNode):
        input = Inputs.input

        class Outputs(BaseOutputs):
            output: str

    @BaseRetryNodeDisplay.wrap(max_attempts=3)
    class InnerRetryGenericNodeDisplay(BaseNodeDisplay[InnerRetryGenericNode]):
        pass

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
            "id": "93572a37-c28e-41ec-8ed0-328200d3fc5e",
            "label": "Inner Retry Generic Node",
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
            "trigger": {"id": "f642862d-2f8a-47b1-b23f-21f26ccfb2cc", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "66374ff9-7b8a-4255-ab48-8971cf4101ba", "name": "default", "type": "DEFAULT"}],
            "adornments": [
                {
                    "id": "5be7d260-74f7-4734-b31b-a46a94539586",
                    "label": "Retry Node",
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
                    "id": "016fa09c-3b6f-49c3-a177-5f1bb1afbeb2",
                    "name": "input",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": str(input_id)},
                }
            ],
            "outputs": [
                {
                    "id": "78eece53-8a20-40a1-8a86-ffebe256282b",
                    "name": "output",
                    "type": "STRING",
                    "value": None,
                    "schema": {"type": "string"},
                }
            ],
        },
        serialized_node,
    )


def test_serialize_node__retry__no_display():
    # GIVEN an adornment node
    @RetryNode.wrap(max_attempts=5)
    class StartNode(BaseNode):
        pass

    # AND a workflow that uses the adornment node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    exec_config = workflow_display.serialize()

    # THEN the workflow display is created successfully
    assert exec_config is not None


def test_serialize_node__try(serialize_node):
    @TryNode.wrap()
    class InnerTryGenericNode(BaseNode):
        input = Inputs.input

        class Outputs(BaseOutputs):
            output: str

    @BaseTryNodeDisplay.wrap()
    class InnerTryGenericNodeDisplay(BaseNodeDisplay[InnerTryGenericNode]):
        pass

    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=InnerTryGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
        global_node_displays={
            InnerTryGenericNode.__wrapped_node__: InnerTryGenericNodeDisplay,
        },
    )

    assert not DeepDiff(
        {
            "id": str(InnerTryGenericNode.__wrapped_node__.__id__),
            "label": "Inner Try Generic Node",
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
            "trigger": {"id": "596c162f-98fd-499a-a2ff-aa576cd8458a", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [{"id": "ee8c7891-0125-4f5c-b5b0-6e3f51bc0e09", "name": "default", "type": "DEFAULT"}],
            "adornments": [
                {
                    "id": "3344083c-a32c-4a32-920b-0fb5093448fa",
                    "label": "Try Node",
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
                    "id": "66a1a015-948e-4b9d-8746-f766fa70a445",
                    "name": "input",
                    "value": {"type": "WORKFLOW_INPUT", "input_variable_id": str(input_id)},
                }
            ],
            "outputs": [
                {
                    "id": "d8d0c9a8-0804-4b43-a874-28a7e7d6aec8",
                    "name": "output",
                    "type": "STRING",
                    "value": None,
                    "schema": {"type": "string"},
                }
            ],
        },
        serialized_node,
    )


def test_serialize_node__try__no_display():
    # GIVEN an adornment node
    @TryNode.wrap()
    class StartNode(BaseNode):
        pass

    # AND a workflow that uses the adornment node
    class MyWorkflow(BaseWorkflow):
        graph = StartNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)

    exec_config = workflow_display.serialize()

    # THEN the workflow display is created successfully
    assert exec_config is not None


def test_serialize_node__stacked():
    @TryNode.wrap()
    @RetryNode.wrap(max_attempts=5)
    class InnerStackedGenericNode(BaseNode):
        pass

    # AND a workflow that uses the adornment node
    class StackedWorkflow(BaseWorkflow):
        graph = InnerStackedGenericNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=StackedWorkflow)
    exec_config = workflow_display.serialize()

    # THEN the workflow display is created successfully
    assert isinstance(exec_config["workflow_raw_data"], dict)
    assert isinstance(exec_config["workflow_raw_data"]["nodes"], list)
    inner_stacked_generic_node = [
        node
        for node in exec_config["workflow_raw_data"]["nodes"]
        if isinstance(node, dict) and node["type"] == "GENERIC"
    ][0]
    assert not DeepDiff(
        {
            "id": "957df57c-42bc-44af-9a31-ce7ac3bb1b8a",
            "label": "Inner Stacked Generic Node",
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
            "trigger": {
                "id": "65595aa4-f5d7-4462-8074-2bd8eb9dc6ee",
                "merge_behavior": "AWAIT_ATTRIBUTES",
            },
            "ports": [{"id": "aebdab62-838e-427a-9de9-301c98472bd4", "name": "default", "type": "DEFAULT"}],
            "adornments": [
                {
                    "id": "2e22c747-9b17-4029-b2ee-e22e22056e1f",
                    "label": "Try Node",
                    "base": {
                        "name": "TryNode",
                        "module": ["vellum", "workflows", "nodes", "core", "try_node", "node"],
                    },
                    "attributes": [
                        {
                            "id": "205b2e6c-1f49-459c-8ed6-58e1b012e5e7",
                            "name": "on_error_code",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        }
                    ],
                },
                {
                    "id": "3149e684-69cf-4909-ae68-c14d101b689f",
                    "label": "Retry Node",
                    "base": {
                        "name": "RetryNode",
                        "module": ["vellum", "workflows", "nodes", "core", "retry_node", "node"],
                    },
                    "attributes": [
                        {
                            "id": "0b10be3f-c221-4f92-9930-7a382390963f",
                            "name": "max_attempts",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 5.0}},
                        },
                        {
                            "id": "24f2a261-45fc-41bb-b700-e2346a0b785b",
                            "name": "delay",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                        {
                            "id": "64c268c4-3fed-4a9f-b22b-959f7921e165",
                            "name": "retry_on_error_code",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                        {
                            "id": "d17f61e6-0b43-45e4-b204-39f82a562fee",
                            "name": "retry_on_condition",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                    ],
                },
            ],
            "attributes": [],
            "outputs": [],
        },
        inner_stacked_generic_node,
    )


def test_serialize_node__adornment_order_matches_decorator_order():
    """
    Tests that adornments are serialized in the same order as decorators are applied.
    """

    @TryNode.wrap()
    @RetryNode.wrap(max_attempts=3)
    class MyNode(BaseNode):
        pass

    # AND a workflow that uses the decorated node
    class MyWorkflow(BaseWorkflow):
        graph = MyNode

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    exec_config = cast(Dict[str, Any], workflow_display.serialize())

    # THEN the workflow should serialize successfully
    assert isinstance(exec_config["workflow_raw_data"], dict)
    assert isinstance(exec_config["workflow_raw_data"]["nodes"], list)

    # AND we should find our decorated node
    nodes = cast(List[Dict[str, Any]], exec_config["workflow_raw_data"]["nodes"])
    my_node = [node for node in nodes if isinstance(node, dict) and node["type"] == "GENERIC"][0]

    adornments = cast(List[Dict[str, Any]], my_node["adornments"])
    assert len(adornments) == 2
    assert adornments[0]["label"] == "Try Node"
    assert adornments[1]["label"] == "Retry Node"


def test_serialize_workflow__retry_node_edges():
    """
    Tests that both retry-adorned nodes are correctly serialized in the nodes array.
    """

    @RetryNode.wrap(max_attempts=3, delay=60)
    class FirstNode(BaseNode):
        class Outputs(BaseOutputs):
            value: str

    @RetryNode.wrap(max_attempts=5, delay=120)
    class SecondNode(BaseNode):
        class Outputs(BaseOutputs):
            result: str

    class MyWorkflow(BaseWorkflow):
        graph = FirstNode >> SecondNode

    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    exec_config = cast(Dict[str, Any], workflow_display.serialize())

    assert isinstance(exec_config["workflow_raw_data"], dict)
    assert isinstance(exec_config["workflow_raw_data"]["nodes"], list)

    nodes = cast(List[Dict[str, Any]], exec_config["workflow_raw_data"]["nodes"])

    generic_nodes = [node for node in nodes if node["type"] == "GENERIC"]
    assert len(generic_nodes) == 2
