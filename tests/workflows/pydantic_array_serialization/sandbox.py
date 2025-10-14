from pydantic import BaseModel

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.state.base import BaseState


class CustomItem(BaseModel):
    """A custom Pydantic model for testing serialization."""

    name: str
    value: int
    is_active: bool = True


class ProcessItemsNode(CodeExecutionNode[BaseState, str]):
    """A code execution node that processes an array of Pydantic models."""

    code = """
def main(items: list) -> str:
    total = sum(item['value'] for item in items)
    active_count = sum(1 for item in items if item.get('is_active', True))
    return f"Processed {len(items)} items: total={total}, active={active_count}"
"""
    code_inputs = {
        "items": [
            CustomItem(name="item1", value=10, is_active=True),
            CustomItem(name="item2", value=20, is_active=False),
            CustomItem(name="item3", value=30),
        ]
    }


class PydanticArrayWorkflow(BaseWorkflow):
    """A workflow demonstrating serialization of an array of Pydantic models."""

    graph = ProcessItemsNode

    class Outputs(BaseWorkflow.Outputs):
        result = ProcessItemsNode.Outputs.result
