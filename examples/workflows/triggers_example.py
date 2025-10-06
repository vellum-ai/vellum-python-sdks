"""
Example demonstrating BaseTrigger and ManualTrigger usage.

This example shows how triggers integrate with the workflow graph system.
"""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers import ManualTrigger


class Inputs(BaseInputs):
    message: str


# Example 1: Explicit ManualTrigger (equivalent to implicit)
class ProcessNode(BaseNode):
    message = Inputs.message

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self):
        return self.Outputs(result=f"Processed: {self.message}")


class ExplicitTriggerWorkflow(BaseWorkflow[Inputs, BaseState]):
    """Workflow with explicit ManualTrigger - same as default behavior."""

    graph = ManualTrigger() >> ProcessNode

    class Outputs(BaseWorkflow.Outputs):
        result = ProcessNode.Outputs.result


# Example 2: Trigger to multiple nodes
class TopNode(BaseNode):
    message = Inputs.message

    class Outputs(BaseNode.Outputs):
        output: str

    def run(self):
        return self.Outputs(output=f"Top: {self.message}")


class BottomNode(BaseNode):
    message = Inputs.message

    class Outputs(BaseNode.Outputs):
        output: str

    def run(self):
        return self.Outputs(output=f"Bottom: {self.message}")


class MergeNode(BaseNode):
    top = TopNode.Outputs.output
    bottom = BottomNode.Outputs.output

    class Outputs(BaseNode.Outputs):
        combined: str

    def run(self):
        return self.Outputs(combined=f"{self.top} + {self.bottom}")


class MultiEntrypointWorkflow(BaseWorkflow[Inputs, BaseState]):
    """Workflow where trigger activates multiple nodes simultaneously."""

    graph = ManualTrigger() >> {TopNode, BottomNode} >> MergeNode

    class Outputs(BaseWorkflow.Outputs):
        result = MergeNode.Outputs.combined


# Example 3: Trigger then chain
class StartNode(BaseNode):
    message = Inputs.message

    class Outputs(BaseNode.Outputs):
        output: str

    def run(self):
        return self.Outputs(output=f"Started: {self.message}")


class MiddleNode(BaseNode):
    input_text = StartNode.Outputs.output

    class Outputs(BaseNode.Outputs):
        output: str

    def run(self):
        return self.Outputs(output=f"{self.input_text} -> Middle")


class EndNode(BaseNode):
    input_text = MiddleNode.Outputs.output

    class Outputs(BaseNode.Outputs):
        final: str

    def run(self):
        return self.Outputs(final=f"{self.input_text} -> End")


class ChainedWorkflow(BaseWorkflow[Inputs, BaseState]):
    """Workflow with trigger followed by a chain of nodes."""

    graph = ManualTrigger() >> StartNode >> MiddleNode >> EndNode

    class Outputs(BaseWorkflow.Outputs):
        result = EndNode.Outputs.final


if __name__ == "__main__":
    # Run example 1
    print("Example 1: Explicit ManualTrigger")
    workflow1 = ExplicitTriggerWorkflow()
    result1 = workflow1.run(inputs=Inputs(message="Hello"))
    print(f"Result: {result1.body.outputs.result}\n")

    # Run example 2
    print("Example 2: Multi-entrypoint")
    workflow2 = MultiEntrypointWorkflow()
    result2 = workflow2.run(inputs=Inputs(message="World"))
    print(f"Result: {result2.body.outputs.result}\n")

    # Run example 3
    print("Example 3: Chained")
    workflow3 = ChainedWorkflow()
    result3 = workflow3.run(inputs=Inputs(message="Chain"))
    print(f"Result: {result3.body.outputs.result}\n")

    # Show graph structure
    print("Graph has triggers:")
    for trigger in workflow1.get_subgraphs()[0].triggers:
        print(f"  - {trigger}")
