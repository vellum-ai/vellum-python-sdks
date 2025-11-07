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
            "id": "9f275cfd-3446-4bb8-a6c2-1632724adc30",
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
            "trigger": {"id": "15a7923e-fed8-4301-a25f-440a30f10a0d", "merge_behavior": "AWAIT_ATTRIBUTES"},
            "ports": [
                {
                    "id": "ccd60c7f-be3a-4616-8aa2-9bcc02f6232a",
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
            "id": "0c58b55b-9ccf-46eb-ab64-bf8904c54a3f",
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
            "trigger": {"id": "a342830b-fe12-4460-9291-c8b31eeb3079", "merge_behavior": "AWAIT_ANY"},
            "ports": [
                {
                    "id": "940e2f08-ccf6-436f-9cb4-aa288de80420",
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
            "id": "97ac6add-c1fc-4e8b-ba5d-2a76c2cf0f55",
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
            "trigger": {"id": "531de423-8c70-4c13-9ed4-dbecf0e85e2e", "merge_behavior": "AWAIT_ALL"},
            "ports": [
                {
                    "id": "b33884e3-b8fb-463b-b6f4-6a7156c75ba3",
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
