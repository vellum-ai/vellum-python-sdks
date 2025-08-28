from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.web_search_node import WebSearchNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState


class ComplexWebSearchInputs(BaseInputs):
    base_query: str
    result_limit: int
    search_location: str


class FirstSearchNode(WebSearchNode):
    query = ComplexWebSearchInputs.base_query
    api_key = VellumSecretReference("SERPAPI_KEY")  # type: ignore[assignment]
    num_results = ComplexWebSearchInputs.result_limit
    location = ComplexWebSearchInputs.search_location


class SecondSearchNode(WebSearchNode):
    query = FirstSearchNode.Outputs.text  # Use output from first search
    api_key = "hardcoded-api-key"  # Constant value
    num_results = 3
    location = None  # None value


class ComplexWebSearchWorkflow(BaseWorkflow[ComplexWebSearchInputs, BaseState]):
    graph = FirstSearchNode >> SecondSearchNode

    class Outputs(BaseWorkflow.Outputs):
        initial_results = FirstSearchNode.Outputs.text
        initial_urls = FirstSearchNode.Outputs.urls
        followup_results = SecondSearchNode.Outputs.text
        all_raw_data = SecondSearchNode.Outputs.results
