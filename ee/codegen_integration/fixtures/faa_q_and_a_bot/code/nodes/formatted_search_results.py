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

    class Display(TemplatingNode.Display):
        x = 3923.3878883718644
        y = -458.89620665696896
