from vellum.workflows.nodes.displayable import MapNode as BaseMapNode

from ...inputs import Inputs
from .workflow import MapNodeWorkflow


class MapNode(BaseMapNode):
    items = Inputs.items
    subworkflow = MapNodeWorkflow
    max_concurrency = 4
