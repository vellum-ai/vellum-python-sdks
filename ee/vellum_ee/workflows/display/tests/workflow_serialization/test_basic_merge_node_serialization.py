from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_merge_node.await_all_workflow import AwaitAllPassingWorkflow


def test_serialize_workflow__await_all():
    # GIVEN a Workflow that uses an await all merge node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=AwaitAllPassingWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 0

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert not DeepDiff(
        [
            {"id": "959ba00d-d30b-402e-8676-76efc4c3d2ae", "key": "value", "type": "STRING"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 6
    assert len(workflow_raw_data["nodes"]) == 6

    # AND each node should be serialized correctly
    entrypoint_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "ENTRYPOINT")
    assert entrypoint_node == {
        "id": "dc8aecd0-49ba-4464-a45f-29d3bfd686e4",
        "type": "ENTRYPOINT",
        "base": None,
        "definition": None,
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "017d40f5-8326-4e42-a409-b08995defaa8",
        },
        "display_data": {
            "position": {"x": 0.0, "y": -50.0},
        },
    }

    passthrough_nodes = [node for node in workflow_raw_data["nodes"] if node["type"] == "GENERIC"]
    assert len(passthrough_nodes) == 3

    merge_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "MERGE")
    assert not DeepDiff(
        {
            "id": "f07c263c-65a3-4b58-83c1-f4a29123f167",
            "type": "MERGE",
            "inputs": [],
            "data": {
                "label": "Await All Merge Node",
                "merge_strategy": "AWAIT_ALL",
                "target_handles": [
                    {"id": "4441c835-7d16-4c43-8599-e948b57eaab1"},
                    {"id": "6da3e50a-8c6d-4de1-8ee9-da26f7c9552f"},
                ],
                "source_handle_id": "da1bdfe9-8e99-4d06-842f-a76af95a713a",
            },
            "display_data": {"position": {"x": 400.0, "y": -50.0}},
            "base": {
                "module": ["vellum", "workflows", "nodes", "displayable", "merge_node", "node"],
                "name": "MergeNode",
            },
            "definition": {
                "module": ["tests", "workflows", "basic_merge_node", "await_all_workflow"],
                "name": "AwaitAllMergeNode",
            },
            "trigger": {
                "id": "1c68b622-cc93-4678-a0c4-89f06b6cad1f",
                "merge_behavior": "AWAIT_ALL",
            },
            "ports": [{"id": "da1bdfe9-8e99-4d06-842f-a76af95a713a", "name": "default", "type": "DEFAULT"}],
        },
        merge_node,
        ignore_order_func=lambda x: x.path() == "root['data']['target_handles']",
    )

    final_output_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "TERMINAL")
    assert final_output_node == {
        "id": "8187ce10-62b7-4a2c-8c0f-297387915467",
        "type": "TERMINAL",
        "data": {
            "label": "Final Output",
            "name": "value",
            "target_handle_id": "ff55701c-16d3-4348-a633-6a298e71377d",
            "output_id": "959ba00d-d30b-402e-8676-76efc4c3d2ae",
            "output_type": "STRING",
            "node_input_id": "fed9d343-6504-460c-968b-d3f9658193d0",
        },
        "base": {
            "module": [
                "vellum",
                "workflows",
                "nodes",
                "displayable",
                "final_output_node",
                "node",
            ],
            "name": "FinalOutputNode",
        },
        "definition": None,
        "inputs": [
            {
                "id": "fed9d343-6504-460c-968b-d3f9658193d0",
                "key": "node_input",
                "value": {
                    "rules": [
                        {
                            "type": "NODE_OUTPUT",
                            "data": {
                                "node_id": "6c34a839-552b-436d-ba6a-501f663883c8",
                                "output_id": "f6148c39-9ec1-4b10-9d24-d19bec9eeea8",
                            },
                        }
                    ],
                    "combinator": "OR",
                },
            }
        ],
        "display_data": {"position": {"x": 800.0, "y": -50.0}},
    }

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "ea747507-68d5-4c72-8d00-a464ff7a55f1",
                "source_node_id": "dc8aecd0-49ba-4464-a45f-29d3bfd686e4",
                "source_handle_id": "017d40f5-8326-4e42-a409-b08995defaa8",
                "target_node_id": "0871708d-8f05-4bc8-b3fb-a8624dae51de",
                "target_handle_id": "01543a95-6bcb-46e2-a16c-570008972b88",
                "type": "DEFAULT",
            },
            {
                "id": "2c28f06b-4f4a-4531-8cf9-860089ce1cc2",
                "source_node_id": "dc8aecd0-49ba-4464-a45f-29d3bfd686e4",
                "source_handle_id": "017d40f5-8326-4e42-a409-b08995defaa8",
                "target_node_id": "0306d2a2-8e2a-49d1-bc4d-4026fbd98c4c",
                "target_handle_id": "5b10f22e-ae81-4ca5-a682-12d3c3ec73c1",
                "type": "DEFAULT",
            },
            {
                "id": "3870f290-8da7-43a8-b875-60510c060380",
                "source_node_id": "0306d2a2-8e2a-49d1-bc4d-4026fbd98c4c",
                "source_handle_id": "4e76416e-4edf-4a4a-9202-bf3ee35fd911",
                "target_node_id": "f07c263c-65a3-4b58-83c1-f4a29123f167",
                "target_handle_id": "4441c835-7d16-4c43-8599-e948b57eaab1",
                "type": "DEFAULT",
            },
            {
                "id": "e89010d4-1f5a-4db9-8b67-1fa68960b142",
                "source_node_id": "0871708d-8f05-4bc8-b3fb-a8624dae51de",
                "source_handle_id": "c11fe2da-9ccd-4434-9330-5e3760abe849",
                "target_node_id": "f07c263c-65a3-4b58-83c1-f4a29123f167",
                "target_handle_id": "6da3e50a-8c6d-4de1-8ee9-da26f7c9552f",
                "type": "DEFAULT",
            },
            {
                "id": "5344fbf3-6a71-4890-93a6-c6a2c5a4e50c",
                "source_node_id": "f07c263c-65a3-4b58-83c1-f4a29123f167",
                "source_handle_id": "da1bdfe9-8e99-4d06-842f-a76af95a713a",
                "target_node_id": "6c34a839-552b-436d-ba6a-501f663883c8",
                "target_handle_id": "413c3699-a37b-49cd-93fd-fe6d041a0119",
                "type": "DEFAULT",
            },
            {
                "id": "3d031c93-09b1-4937-9f98-c30a7ba6823d",
                "source_node_id": "6c34a839-552b-436d-ba6a-501f663883c8",
                "source_handle_id": "48beca40-00f3-4273-b2ea-5e1ac6494839",
                "target_node_id": "8187ce10-62b7-4a2c-8c0f-297387915467",
                "target_handle_id": "ff55701c-16d3-4348-a633-6a298e71377d",
                "type": "DEFAULT",
            },
        ],
        serialized_edges,
        ignore_order=True,
    )

    # AND the display data should be what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {
        "viewport": {
            "x": 0.0,
            "y": 0.0,
            "zoom": 1.0,
        }
    }

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "AwaitAllPassingWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_merge_node",
            "await_all_workflow",
        ],
    }
