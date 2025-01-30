from typing import Generic, TypeVar

from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay

_RetryNodeType = TypeVar("_RetryNodeType", bound=RetryNode)


class BaseRetryNodeDisplay(BaseNodeDisplay[_RetryNodeType], Generic[_RetryNodeType]):
    pass
