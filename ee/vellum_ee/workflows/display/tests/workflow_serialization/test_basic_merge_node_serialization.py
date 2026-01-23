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
            "position": {"x": 0.0, "y": 0.0},
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
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
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

    # AND each edge feeding into the merge node should be serialized correctly
    merge_target_edges = [edge for edge in workflow_raw_data["edges"] if edge["target_node_id"] == merge_node["id"]]
    assert not DeepDiff(
        [
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
        ],
        merge_target_edges,
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
