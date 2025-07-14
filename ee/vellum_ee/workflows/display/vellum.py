from typing import List, Literal

from vellum.client.core import UniversalBaseModel
from vellum_ee.workflows.display.base import WorkflowDisplayData  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.base import WorkflowDisplayDataViewport  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.editor.types import NodeDisplayData  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.editor.types import NodeDisplayPosition  # noqa: F401 - Remove in 0.15.0
from vellum_ee.workflows.display.utils.vellum import NodeInputValuePointerRule


class NodeInputValuePointer(UniversalBaseModel):
    rules: List[NodeInputValuePointerRule]
    combinator: Literal["OR"] = "OR"


class NodeInput(UniversalBaseModel):
    id: str
    key: str
    value: NodeInputValuePointer
