from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable import SearchNode
from vellum.workflows.nodes.displayable.bases.types import (
    MetadataLogicalCondition,
    MetadataLogicalConditionGroup,
    SearchFilters,
)
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_search_filters_with_input_reference():
    """Test that SearchFilters with MetadataLogicalCondition using input references can be serialized"""

    # GIVEN a search node with a metadata filter that uses an input reference
    class TestInputs(BaseInputs):
        file_id: str

    class MySearchNode(SearchNode):
        query = "my query"
        document_index = "document_index"
        filters = SearchFilters(
            external_ids=None,
            metadata=MetadataLogicalConditionGroup(
                combinator="AND",
                negated=False,
                conditions=[MetadataLogicalCondition(lhs_variable="ID", operator="=", rhs_variable=TestInputs.file_id)],
            ),
        )

    # AND a workflow with the Search Node
    class Workflow(BaseWorkflow[TestInputs, BaseState]):
        graph = MySearchNode

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=Workflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the node should properly serialize the filter reference
    serialized_search_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["id"] == str(MySearchNode.__id__)
    )

    serialized_metadata_filter = next(
        inp for inp in serialized_search_node["inputs"] if inp["key"] == "metadata_filters"
    )

    assert serialized_metadata_filter == {
        "id": "75cd40e5-dd40-4d45-bff6-b6a674007033",
        "key": "metadata_filters",
        "value": {
            "combinator": "OR",
            "rules": [
                {
                    "data": {
                        "type": "JSON",
                        "value": {
                            "combinator": "AND",
                            "conditions": [
                                {
                                    "lhs_variable_id": "08f0f43d-6374-4922-945c-25353fdc4f94",
                                    "operator": "=",
                                    "rhs_variable_id": "59c278e2-6371-4392-b912-fe15af5e907e",
                                    "type": "LOGICAL_CONDITION",
                                }
                            ],
                            "negated": False,
                            "type": "LOGICAL_CONDITION_GROUP",
                        },
                    },
                    "type": "CONSTANT_VALUE",
                }
            ],
        },
    }

    # AND the LHS filter references should be present as node inputs
    serialized_lhs_input = next(
        inp for inp in serialized_search_node["inputs"] if inp["id"] == "08f0f43d-6374-4922-945c-25353fdc4f94"
    )
    assert serialized_lhs_input["value"] == {
        "combinator": "OR",
        "rules": [
            {
                "data": {"type": "STRING", "value": "ID"},
                "type": "CONSTANT_VALUE",
            }
        ],
    }

    # AND the RHS filter references should be present as node inputs
    serialized_rhs_input = next(
        inp for inp in serialized_search_node["inputs"] if inp["id"] == "59c278e2-6371-4392-b912-fe15af5e907e"
    )
    assert serialized_rhs_input["value"] == {
        "combinator": "OR",
        "rules": [
            {
                "data": {"input_variable_id": "e2f4fff9-1277-47cb-8988-12f8ada450ba"},
                "type": "INPUT_VARIABLE",
            }
        ],
    }
