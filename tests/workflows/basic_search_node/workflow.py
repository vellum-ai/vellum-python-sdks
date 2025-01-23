from vellum import (
    SearchFiltersRequest,
    SearchRequestOptionsRequest,
    SearchWeightsRequest,
    StringVellumValueRequest,
    VellumValueLogicalConditionGroupRequest,
    VellumValueLogicalConditionRequest,
)
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import SearchNode
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    query: str


class SimpleSearchNode(SearchNode):
    query = Inputs.query
    document_index = "name"
    weights = SearchWeightsRequest(semantic_similarity=0.55, keywords=0.45)
    options = SearchRequestOptionsRequest(
        filters=SearchFiltersRequest(
            external_ids=None,
            metadata=VellumValueLogicalConditionGroupRequest(
                type="LOGICAL_CONDITION_GROUP",
                combinator="AND",
                negated=False,
                conditions=[
                    VellumValueLogicalConditionRequest(
                        type="LOGICAL_CONDITION",
                        lhs_variable=StringVellumValueRequest(
                            type="STRING", value="a6322ca2-8b65-4d26-b3a1-f926dcada0fa"
                        ),
                        operator="=",
                        rhs_variable=StringVellumValueRequest(
                            type="STRING", value="c539a2e2-0873-43b0-ae21-81790bb1c4cb"
                        ),
                    ),
                    VellumValueLogicalConditionRequest(
                        type="LOGICAL_CONDITION",
                        lhs_variable=StringVellumValueRequest(
                            type="STRING", value="a89483b6-6850-4105-8c4e-ec0fd197cd43"
                        ),
                        operator="=",
                        rhs_variable=StringVellumValueRequest(
                            type="STRING", value="847b8ee0-2c37-4e41-9dea-b4ba3579e2c1"
                        ),
                    ),
                ],
            ),
        ),
    )
    chunk_separator = "\n\n#####\n\n"


class BasicSearchWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = SimpleSearchNode

    class Outputs(BaseWorkflow.Outputs):
        text = SimpleSearchNode.Outputs.text
