from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .help_docs_lookup import HelpDocsLookup


class GetSearchResultsWithMetadata(TemplatingNode[BaseState, str]):
    template = """{{ docs_context }}"""
    inputs = {
        "docs_context": HelpDocsLookup.Outputs.results,
    }
