from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.map_node.node import MapNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


class Inputs(BaseInputs):
    foo: str


class State(BaseState):
    bar: str


@MapNode.wrap(items=[1, 2, 3])
class MapGenericNode(BaseNode):
    item = MapNode.SubworkflowInputs.item
    foo = Inputs.foo
    bar = State.bar

    class Outputs(BaseOutputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value=f"{self.foo} {self.bar} {self.item}")


class MapGenericNodeWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    graph = {MapGenericNode}


def test_serialize_node__map():
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=MapGenericNodeWorkflow
    )
    serialized_workflow: dict = workflow_display.serialize()
    assert not DeepDiff(
        {
            "workflow_raw_data": {
                "nodes": [
                    {
                        "id": "08de39f4-3019-455a-bc6c-331ae19c6e2a",
                        "type": "ENTRYPOINT",
                        "inputs": [],
                        "data": {
                            "label": "Entrypoint Node",
                            "source_handle_id": "9c071b05-0071-4897-a0d8-ba68913de5e1",
                        },
                        "display_data": {"position": {"x": 0.0, "y": 0.0}},
                        "base": None,
                        "definition": None,
                    },
                    {
                        "id": "527a10bc-30b2-4e36-91d6-91c8e865bac8",
                        "type": "MAP",
                        "inputs": [
                            {
                                "id": "5771822f-86c8-4f98-a79d-1a8567a1800b",
                                "key": "items",
                                "value": {
                                    "rules": [{"type": "CONSTANT_VALUE", "data": {"type": "JSON", "value": [1, 2, 3]}}],
                                    "combinator": "OR",
                                },
                            }
                        ],
                        "data": {
                            "label": "Map Node",
                            "error_output_id": None,
                            "source_handle_id": "c59be5f3-c304-4763-afdc-1d775f9e1a05",
                            "target_handle_id": "3a702aac-7b68-47d3-92e1-264883e9532c",
                            "variant": "INLINE",
                            "workflow_raw_data": {
                                "nodes": [
                                    {
                                        "id": "e9689479-745e-41e0-9516-8c077fdbc7de",
                                        "type": "ENTRYPOINT",
                                        "inputs": [],
                                        "data": {
                                            "label": "Entrypoint Node",
                                            "source_handle_id": "4bd5ba28-f0b7-478c-97bc-015c84557557",
                                        },
                                        "display_data": {"position": {"x": 0.0, "y": 0.0}},
                                        "base": None,
                                        "definition": None,
                                    },
                                    {
                                        "id": "ff5b8b34-dd8b-4900-8b4c-0175ad6489e9",
                                        "type": "TERMINAL",
                                        "data": {
                                            "label": "Final Output",
                                            "name": "value",
                                            "target_handle_id": "6fbe546a-d516-47a8-9bad-c4361a0d0911",
                                            "output_id": "319d604f-e435-45c0-999d-73a5f1d37fd1",
                                            "output_type": "STRING",
                                            "node_input_id": "4c4a3b61-8bfe-4803-8f7b-daedae025b32",
                                        },
                                        "inputs": [
                                            {
                                                "id": "4c4a3b61-8bfe-4803-8f7b-daedae025b32",
                                                "key": "node_input",
                                                "value": {
                                                    "rules": [
                                                        {
                                                            "type": "NODE_OUTPUT",
                                                            "data": {
                                                                "node_id": "862bbecb-6eb4-4b65-99c2-e8a5d72a742d",
                                                                "output_id": "6aaf397f-a3e2-4a1d-a2ae-58f945d91ecc",
                                                            },
                                                        }
                                                    ],
                                                    "combinator": "OR",
                                                },
                                            }
                                        ],
                                        "display_data": {"position": {"x": 0.0, "y": 0.0}},
                                        "base": {
                                            "name": "FinalOutputNode",
                                            "module": [
                                                "vellum",
                                                "workflows",
                                                "nodes",
                                                "displayable",
                                                "final_output_node",
                                                "node",
                                            ],
                                        },
                                        "definition": None,
                                    },
                                ],
                                "edges": [
                                    {
                                        "id": "716c0f7f-7636-40b1-972c-59f9b0200774",
                                        "source_node_id": "e9689479-745e-41e0-9516-8c077fdbc7de",
                                        "source_handle_id": "4bd5ba28-f0b7-478c-97bc-015c84557557",
                                        "target_node_id": "862bbecb-6eb4-4b65-99c2-e8a5d72a742d",
                                        "target_handle_id": "a568a8fb-fd40-4cd1-bfb6-c829664857de",
                                        "type": "DEFAULT",
                                    },
                                    {
                                        "id": "dc2ede20-6f04-43d3-b5cd-305814aa9fca",
                                        "source_node_id": "862bbecb-6eb4-4b65-99c2-e8a5d72a742d",
                                        "source_handle_id": "c59be5f3-c304-4763-afdc-1d775f9e1a05",
                                        "target_node_id": "ff5b8b34-dd8b-4900-8b4c-0175ad6489e9",
                                        "target_handle_id": "6fbe546a-d516-47a8-9bad-c4361a0d0911",
                                        "type": "DEFAULT",
                                    },
                                ],
                                "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
                                "definition": {
                                    "name": "Subworkflow",
                                    "module": ["vellum", "workflows", "nodes", "utils"],
                                },
                            },
                            "input_variables": [],
                            "output_variables": [
                                {"id": "319d604f-e435-45c0-999d-73a5f1d37fd1", "key": "value", "type": "STRING"}
                            ],
                            "concurrency": None,
                            "items_input_id": None,
                            "item_input_id": None,
                            "index_input_id": None,
                        },
                        "display_data": {"position": {"x": 0.0, "y": 0.0}},
                        "base": {
                            "name": "MapNode",
                            "module": ["vellum", "workflows", "nodes", "core", "map_node", "node"],
                        },
                        "definition": {
                            "name": "MapNode",
                            "module": [
                                "vellum_ee",
                                "workflows",
                                "display",
                                "tests",
                                "workflow_serialization",
                                "generic_nodes",
                                "test_adornments_serialization",
                                "MapGenericNode",
                                "<adornment>",
                            ],
                        },
                    },
                ],
                "edges": [
                    {
                        "id": "c2df60be-be62-4d57-b6b3-6d5b23aa5790",
                        "source_node_id": "08de39f4-3019-455a-bc6c-331ae19c6e2a",
                        "source_handle_id": "9c071b05-0071-4897-a0d8-ba68913de5e1",
                        "target_node_id": "862bbecb-6eb4-4b65-99c2-e8a5d72a742d",
                        "target_handle_id": "a568a8fb-fd40-4cd1-bfb6-c829664857de",
                        "type": "DEFAULT",
                    }
                ],
                "display_data": {"viewport": {"x": 0.0, "y": 0.0, "zoom": 1.0}},
                "definition": {
                    "name": "MapGenericNodeWorkflow",
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
            "output_variables": [],
        },
        serialized_workflow,
        ignore_order=True,
    )
