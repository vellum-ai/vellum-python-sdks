from typing import Generic, TypeVar

from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum_ee.workflows.display.nodes.vellum.base_adornment_node import BaseAdornmentNodeDisplay

_RetryNodeType = TypeVar("_RetryNodeType", bound=RetryNode)


class BaseRetryNodeDisplay(BaseAdornmentNodeDisplay[_RetryNodeType], Generic[_RetryNodeType]):
    pass
