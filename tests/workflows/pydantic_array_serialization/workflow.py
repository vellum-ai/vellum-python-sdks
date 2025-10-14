from typing import List

from pydantic import BaseModel

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class CustomItem(BaseModel):
    """A custom Pydantic model for testing serialization."""

    name: str
    value: int
    is_active: bool = True


class Inputs(BaseInputs):
    items: List[CustomItem]


class ProcessItemsNode(BaseNode):
    """A node that processes an array of Pydantic models."""

    items = Inputs.items

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> BaseOutputs:
        total = sum(item.value for item in self.items)
        active_count = sum(1 for item in self.items if item.is_active)
        return self.Outputs(result=f"Processed {len(self.items)} items: total={total}, active={active_count}")


class PydanticArrayWorkflow(BaseWorkflow[Inputs, BaseState]):
    """A workflow demonstrating serialization of an array of Pydantic models."""

    graph = ProcessItemsNode

    class Outputs(BaseOutputs):
        result = ProcessItemsNode.Outputs.result
