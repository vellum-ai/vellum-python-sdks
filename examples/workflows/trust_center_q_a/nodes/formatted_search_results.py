from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .search_results import SearchResults


class FormattedSearchResults(TemplatingNode[BaseState, str]):
    """Here we format the resulting chunks that we retrieved from the Document Index and include the source document in each formatted chunk so our LLM can cite its source when it gives an answer."""

    template = """\
{% for result in results -%}
Policy {{ result.document.label }}:
------
{{ result.text }}
{% if not loop.last %}

#####

{% endif %}
{% endfor %}\
"""
    inputs = {
        "results": SearchResults.Outputs.results,
    }
