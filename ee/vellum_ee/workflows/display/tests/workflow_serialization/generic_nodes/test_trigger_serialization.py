from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import MergeBehavior
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: str


def test_serialize_node__basic(serialize_node):
    class BasicGenericNode(BaseNode):
        pass

    serialized_node = serialize_node(BasicGenericNode)
    assert not DeepDiff(
        {
            "id": "8d7cbfe4-72ca-4367-a401-8d28723d2f00",
            "label": "Basic Generic Node",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "BasicGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_trigger_serialization",
                ],
            },
            "trigger": {"id": "b95cca96-b570-42ac-ace8-51ca0f627881", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "8bec8d0c-113f-4110-afcb-4a6e566e7236",
                    "name": "default",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__await_any(serialize_node):
    class AwaitAnyGenericNode(BaseNode):
        class Trigger(BaseNode.Trigger):
            merge_behavior = MergeBehavior.AWAIT_ANY

    serialized_node = serialize_node(AwaitAnyGenericNode)
    assert not DeepDiff(
        {
            "id": "42e17f0e-8496-415f-9c72-f85250ba6f0b",
            "label": "Await Any Generic Node",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "AwaitAnyGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_trigger_serialization",
                ],
            },
            "trigger": {"id": "c0db17e7-6766-4062-aaee-7404580d76e4", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "d9a84db7-8bd6-4a15-9e3c-c2e898c26d16",
                    "name": "default",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__await_all(serialize_node):
    class AwaitAllGenericNode(BaseNode):
        class Trigger(BaseNode.Trigger):
            merge_behavior = MergeBehavior.AWAIT_ALL

    serialized_node = serialize_node(AwaitAllGenericNode)
    assert not DeepDiff(
        {
            "id": "b3e1145a-5f41-456b-9382-6d0a1e828c2f",
            "label": "Await All Generic Node",
            "type": "GENERIC",
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {"name": "BaseNode", "module": ["vellum", "workflows", "nodes", "bases", "base"]},
            "definition": {
                "name": "AwaitAllGenericNode",
                "module": [
                    "vellum_ee",
                    "workflows",
                    "display",
                    "tests",
                    "workflow_serialization",
                    "generic_nodes",
                    "test_trigger_serialization",
                ],
            },
            "trigger": {"id": "1b22935e-0e79-485a-b274-a2f316c0983c", "merge_behavior": "AWAIT_ALL"},
            "ports": [
                {
                    "id": "fa73da35-0bf9-4f02-bf5b-0b0d1a6f1494",
                    "name": "default",
                    "type": "DEFAULT",
                }
            ],
            "adornments": None,
            "attributes": [],
            "outputs": [],
        },
        serialized_node,
        ignore_order=True,
    )


def test_serialize_node__inline_prompt_await_all():
    """
    Tests that InlinePromptNode with AWAIT_ALL merge behavior can be defined and serializes without errors.
    """

    # GIVEN an InlinePromptNode with AWAIT_ALL merge behavior
    class AwaitAllInlinePromptNode(InlinePromptNode):
        ml_model = "gpt-4o"
        blocks = []

        class Trigger(InlinePromptNode.Trigger):
            merge_behavior = MergeBehavior.AWAIT_ALL

    class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
        graph = AwaitAllInlinePromptNode

    # WHEN we serialize the workflow containing the node
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized = workflow_display.serialize()

    # THEN the workflow should serialize successfully
    assert "workflow_raw_data" in serialized  # type: ignore
    assert "nodes" in serialized["workflow_raw_data"]  # type: ignore

    # AND the workflow should contain the InlinePromptNode
    nodes = serialized["workflow_raw_data"]["nodes"]  # type: ignore
    prompt_nodes = [node for node in nodes if node["type"] == "PROMPT"]  # type: ignore
    assert len(prompt_nodes) == 1

    prompt_node = prompt_nodes[0]

    # AND the node should have the correct type and base
    assert prompt_node["type"] == "PROMPT"  # type: ignore
    assert prompt_node["base"]["name"] == "InlinePromptNode"  # type: ignore
    assert prompt_node["base"]["module"] == [  # type: ignore
        "vellum",
        "workflows",
        "nodes",
        "displayable",
        "inline_prompt_node",
        "node",
    ]

    # AND the node should have the expected structure (InlinePromptNode doesn't serialize trigger info)
    assert "data" in prompt_node  # type: ignore
    assert "ml_model_name" in prompt_node["data"]  # type: ignore
    assert prompt_node["data"]["ml_model_name"] == "gpt-4o"  # type: ignore

    assert prompt_node["trigger"]["merge_behavior"] == "AWAIT_ALL"  # type: ignore
