from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.web_search_node import WebSearchNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState


class WebSearchInputs(BaseInputs):
    search_query: str


class SimpleWebSearchNode(WebSearchNode):
    query = WebSearchInputs.search_query
    api_key = VellumSecretReference("SERPAPI_KEY")  # type: ignore[assignment]
    num_results = 5
    location = "United States"


class WebSearchWorkflow(BaseWorkflow[WebSearchInputs, BaseState]):
    graph = SimpleWebSearchNode

    class Outputs(BaseWorkflow.Outputs):
        search_results = SimpleWebSearchNode.Outputs.text
        result_urls = SimpleWebSearchNode.Outputs.urls
