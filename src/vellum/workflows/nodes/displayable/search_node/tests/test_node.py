from vellum import SearchResponse, SearchResult, SearchResultDocument
from vellum.client.types.json_vellum_value_request import JsonVellumValueRequest
from vellum.client.types.search_filters_request import SearchFiltersRequest
from vellum.client.types.search_request_options_request import SearchRequestOptionsRequest
from vellum.client.types.search_result_merging_request import SearchResultMergingRequest
from vellum.client.types.search_weights_request import SearchWeightsRequest
from vellum.client.types.string_vellum_value_request import StringVellumValueRequest
from vellum.client.types.vellum_value_logical_condition_group_request import VellumValueLogicalConditionGroupRequest
from vellum.client.types.vellum_value_logical_condition_request import VellumValueLogicalConditionRequest
from vellum.workflows.nodes.displayable.bases.types import (
    MetadataLogicalCondition,
    MetadataLogicalConditionGroup,
    SearchFilters,
)
from vellum.workflows.nodes.displayable.search_node.node import SearchNode


def test_run_workflow__happy_path(vellum_client):
    """Confirm that we can successfully invoke a Workflow with the new option attributes"""

    # GIVEN a workflow that's set up run a Search Node
    class MySearchNode(SearchNode):
        query = "Search query"
        document_index = "document_index"
        limit = 1
        weights = SearchWeightsRequest(
            semantic_similarity=0.8,
            keywords=0.2,
        )
        result_merging = SearchResultMergingRequest(
            enabled=True,
        )
        filters = SearchFilters(
            external_ids=["external_id"],
            metadata=MetadataLogicalConditionGroup(
                combinator="AND",
                negated=False,
                conditions=[
                    MetadataLogicalCondition(
                        lhs_variable="TYPE",
                        operator="=",
                        rhs_variable="COMPANY",
                    ),
                    MetadataLogicalCondition(
                        lhs_variable="NAME",
                        operator="notNull",
                    ),
                ],
            ),
        )

    # AND a Search request that will return a 200 ok resposne
    search_response = SearchResponse(
        results=[
            SearchResult(
                text="Search query", score="0.0", keywords=["keywords"], document=SearchResultDocument(label="label")
            )
        ]
    )

    vellum_client.search.return_value = search_response

    # WHEN we run the workflow
    outputs = MySearchNode().run()

    # THEN the workflow should have completed successfully
    assert outputs.text == "Search query"

    # AND the options should be as expected
    assert vellum_client.search.call_args.kwargs["options"] == SearchRequestOptionsRequest(
        limit=1,
        weights=SearchWeightsRequest(
            semantic_similarity=0.8,
            keywords=0.2,
        ),
        result_merging=SearchResultMergingRequest(
            enabled=True,
        ),
        filters=SearchFiltersRequest(
            external_ids=["external_id"],
            metadata=VellumValueLogicalConditionGroupRequest(
                combinator="AND",
                negated=False,
                conditions=[
                    VellumValueLogicalConditionRequest(
                        lhs_variable=StringVellumValueRequest(value="TYPE"),
                        operator="=",
                        rhs_variable=StringVellumValueRequest(value="COMPANY"),
                    ),
                    VellumValueLogicalConditionRequest(
                        lhs_variable=StringVellumValueRequest(value="NAME"),
                        operator="notNull",
                        rhs_variable=JsonVellumValueRequest(value=None),
                    ),
                ],
            ),
        ),
    )


def test_run_workflow__happy_path__options_attribute(vellum_client):
    """Confirm that we can successfully invoke a single Search node with the legacy options attribute"""

    # GIVEN a workflow that's set up run a Search Node
    class MySearchNode(SearchNode):
        query = "Search query"
        document_index = "document_index"
        options = SearchRequestOptionsRequest(
            limit=1,
            weights=SearchWeightsRequest(
                semantic_similarity=0.8,
                keywords=0.2,
            ),
            result_merging=SearchResultMergingRequest(
                enabled=True,
            ),
            filters=SearchFiltersRequest(
                external_ids=["external_id"],
                metadata=VellumValueLogicalConditionGroupRequest(
                    combinator="AND",
                    negated=False,
                    conditions=[
                        VellumValueLogicalConditionRequest(
                            lhs_variable=StringVellumValueRequest(value="TYPE"),
                            operator="=",
                            rhs_variable=StringVellumValueRequest(value="COMPANY"),
                        )
                    ],
                ),
            ),
        )

    # AND a Search request that will return a 200 ok resposne
    search_response = SearchResponse(
        results=[
            SearchResult(
                text="Search query", score="0.0", keywords=["keywords"], document=SearchResultDocument(label="label")
            )
        ]
    )

    vellum_client.search.return_value = search_response

    # WHEN we run the workflow
    outputs = MySearchNode().run()

    # THEN the workflow should have completed successfully
    assert outputs.text == "Search query"

    # AND the options should be as expected
    assert vellum_client.search.call_args.kwargs["options"] == SearchRequestOptionsRequest(
        limit=1,
        weights=SearchWeightsRequest(
            semantic_similarity=0.8,
            keywords=0.2,
        ),
        result_merging=SearchResultMergingRequest(
            enabled=True,
        ),
        filters=SearchFiltersRequest(
            external_ids=["external_id"],
            metadata=VellumValueLogicalConditionGroupRequest(
                combinator="AND",
                negated=False,
                conditions=[
                    VellumValueLogicalConditionRequest(
                        lhs_variable=StringVellumValueRequest(value="TYPE"),
                        operator="=",
                        rhs_variable=StringVellumValueRequest(value="COMPANY"),
                    )
                ],
            ),
        ),
    )
