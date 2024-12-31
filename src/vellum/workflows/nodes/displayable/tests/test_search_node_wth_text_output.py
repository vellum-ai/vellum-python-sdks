# flake8: noqa: E731, E501

import pytest

from vellum import (
    SearchFiltersRequest,
    SearchRequestOptionsRequest,
    SearchResponse,
    SearchResult,
    SearchResultDocument,
    SearchResultMergingRequest,
    SearchWeightsRequest,
)
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.search_node import SearchNode as BaseSearchNode
from vellum.workflows.state import BaseState
from vellum.workflows.state.base import StateMeta


@pytest.fixture
def vellum_search_client(vellum_client):
    return vellum_client.search


def test_search_node_wth_text_output(vellum_search_client):
    """Confirm that SearchNodes output the expected text and results when run."""

    # GIVEN a node that subclasses SearchNode
    class Inputs(BaseInputs):
        query: str
        document_index: str

    class State(BaseState):
        pass

    class SearchNode(BaseSearchNode):
        query = Inputs.query
        document_index = Inputs.document_index

    # AND a mock Vellum search client that returns the expected results
    expected_results = [
        SearchResult(
            text="A request that is made by a consumer, by a consumer on behalf of the consumer's minor child, \nor by a natural person or a person registered with the Secretary of State, authorized by the \nconsumer to act on the consumer's behalf, and that the business can reasonably verify, pursuant \nto regulations adopted by the Attorney General pursuant to paragraph (7) of subdivision (a) of \nSection 1798.185 to be the consumer about whom the business has collected personal \ninformation. \nA business is not obligated to provide information to the consumer pursuant to \nSections 1798.110 and 1798.115 if the business cannot verify, pursuant this subdivision and \nregulations adopted by the Attorney General pursuant to paragraph (7) of subdivision (a) of \nSection 1798.185, that the consumer making the request is the consumer about whom the \nbusiness has collected information or is a person authorized by the consumer to act on such \nconsumer's behalf.",  # noqa: E501
            score=0.8,
            keywords=["Data Classification Policy - v1.pdf"],
            document=SearchResultDocument(
                id="e6d375ed-96fd-4d24-9f89-b4d5d10bca6b",
                label="Data Classification Policy - v1.pdf",
                external_id="Data Classification Policy - v1.pdf",
                metadata={},
            ),
            meta=None,
        ),
        SearchResult(
            text="To a Law Enforcement Official for Law Enforcement Purposes, under the following conditions: \nO \nPursuant to a process and as otherwise required by law, but only if the information sought is relevant \nand material, the request is specific and limited to amounts reasonably necessary, and it is not \npossible to use de-identified information. \nO \nAn order of a court or administrative tribunal (disclosure must be limited to PHI expressly \nauthorized by the order); and \nA subpoena, discovery request or other lawful process, not accompanied by a court order or \nadministrative tribunal, upon receipt of assurances that the individual has been given notice of the \nrequest, or that the party seeking the information has made reasonable efforts to receive a qualified \nprotective order. Information requested is limited information to identify or locate a suspect, fugitive, material\nwitness or missing person.",  # noqa: E501
            score=0.6347101,
            keywords=["Privacy, Use, and Disclosure Policy - v1.pdf"],
            document=SearchResultDocument(
                id="bd3da448-d94a-4cef-be54-48ffeb019b14",
                label="Privacy, Use, and Disclosure Policy - v1.pdf",
                external_id="Privacy, Use, and Disclosure Policy - v1.pdf",
                metadata={},
            ),
            meta=None,
        ),
    ]
    vellum_search_client.return_value = SearchResponse(results=expected_results)

    # WHEN the node is run
    node = SearchNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(
                    query="How often is employee training?",
                    document_index="vellum-trust-center-policies",
                )
            ),
        )
    )
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert (
        outputs.text
        == """\
A request that is made by a consumer, by a consumer on behalf of the consumer's minor child, 
or by a natural person or a person registered with the Secretary of State, authorized by the 
consumer to act on the consumer's behalf, and that the business can reasonably verify, pursuant 
to regulations adopted by the Attorney General pursuant to paragraph (7) of subdivision (a) of 
Section 1798.185 to be the consumer about whom the business has collected personal 
information. 
A business is not obligated to provide information to the consumer pursuant to 
Sections 1798.110 and 1798.115 if the business cannot verify, pursuant this subdivision and 
regulations adopted by the Attorney General pursuant to paragraph (7) of subdivision (a) of 
Section 1798.185, that the consumer making the request is the consumer about whom the 
business has collected information or is a person authorized by the consumer to act on such 
consumer's behalf.

#####

To a Law Enforcement Official for Law Enforcement Purposes, under the following conditions: 
O 
Pursuant to a process and as otherwise required by law, but only if the information sought is relevant 
and material, the request is specific and limited to amounts reasonably necessary, and it is not 
possible to use de-identified information. 
O 
An order of a court or administrative tribunal (disclosure must be limited to PHI expressly 
authorized by the order); and 
A subpoena, discovery request or other lawful process, not accompanied by a court order or 
administrative tribunal, upon receipt of assurances that the individual has been given notice of the 
request, or that the party seeking the information has made reasonable efforts to receive a qualified 
protective order. Information requested is limited information to identify or locate a suspect, fugitive, material
witness or missing person.\
"""
    )

    assert outputs.results == expected_results

    # AND we should have made the expected call to Vellum search
    vellum_search_client.assert_called_once_with(
        document_index="vellum-trust-center-policies",
        query="How often is employee training?",
        options=SearchRequestOptionsRequest(
            limit=8,
            weights=SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2),
            result_merging=SearchResultMergingRequest(enabled=True),
            filters=SearchFiltersRequest(
                external_ids=None,
                metadata=None,
            ),
        ),
    )
