from vellum.workflows.nodes.displayable import TemplatingNode

from .faa_document_store import FAADocumentStore


class FormattedSearchResults(TemplatingNode[str]):
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
