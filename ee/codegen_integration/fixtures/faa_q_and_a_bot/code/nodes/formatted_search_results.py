from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .faa_document_store import FAADocumentStore


class FormattedSearchResults(TemplatingNode[BaseState, str]):
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
        "results": FAADocumentStore.Outputs.results,
    }
