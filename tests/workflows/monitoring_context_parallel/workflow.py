from typing import List

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class SimpleInputs(BaseInputs):
    items: List[str]


class SimpleState(BaseState):
    processed_items: List[str] = []


class SimpleOutputs(BaseOutputs):
    result: str


class SimpleNode(BaseNode[SimpleState]):
    class Outputs(BaseOutputs):
        processed: str

    def run(self) -> Outputs:
        # This method will be automatically decorated with monitoring context
        current_item = self.state.processed_items[-1] if self.state.processed_items else "default"
        return self.Outputs(processed=f"Processed: {current_item}")


class SimpleWorkflow(BaseWorkflow[SimpleInputs, SimpleState]):
    graph = {SimpleNode}

    class Outputs(SimpleOutputs):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply monitoring decorators to this workflow instance
        from vellum.workflows.monitoring.utils import apply_monitoring_to_instance_methods

        apply_monitoring_to_instance_methods(self, ["run", "stream"])

    def get_default_inputs(self) -> SimpleInputs:
        return SimpleInputs(items=["apple", "banana", "cherry"])

    def get_default_state(self, inputs: SimpleInputs) -> SimpleState:
        return SimpleState(processed_items=inputs.items)
