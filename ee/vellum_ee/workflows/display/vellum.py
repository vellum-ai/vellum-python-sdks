from typing import List, Literal

from vellum.client.core import UniversalBaseModel
from vellum_ee.workflows.display.utils.vellum import NodeInputValuePointerRule


class NodeInputValuePointer(UniversalBaseModel):
    rules: List[NodeInputValuePointerRule]
    combinator: Literal["OR"] = "OR"


class NodeInput(UniversalBaseModel):
    id: str
    key: str
    value: NodeInputValuePointer
