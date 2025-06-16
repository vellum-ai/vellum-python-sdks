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
        "id": "4a9f96aa-ba3b-4c4e-9ce4-370fe64f717f",
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
                                    "lhs_variable_id": "9aedaffa-c2a4-4c37-9969-184e1ff43ded",
                                    "operator": "=",
                                    "rhs_variable_id": "c2151ef1-ad98-4940-b0e9-28dabe47a951",
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
        inp for inp in serialized_search_node["inputs"] if inp["id"] == "9aedaffa-c2a4-4c37-9969-184e1ff43ded"
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
        inp for inp in serialized_search_node["inputs"] if inp["id"] == "c2151ef1-ad98-4940-b0e9-28dabe47a951"
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
