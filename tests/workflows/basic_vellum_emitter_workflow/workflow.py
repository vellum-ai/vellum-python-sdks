from vellum.workflows import BaseWorkflow
from vellum.workflows.emitters import VellumEmitter
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class State(BaseState):
    score = 0


class StartNode(BaseNode):
    class Outputs(BaseOutputs):
        final_value: str

    def run(self) -> Outputs:
        return self.Outputs(final_value="Hello, World!")


class NextNode(BaseNode[State]):
    start_node_output = StartNode.Outputs.final_value

    class Outputs(BaseOutputs):
        final_value: str

    def run(self) -> Outputs:
        self.state.score = len(self.start_node_output)
        return self.Outputs(final_value=f"Score: {self.state.score}")


class BasicVellumEmitterWorkflow(BaseWorkflow[BaseInputs, State]):
    """
    Basic workflow that demonstrates VellumEmitter usage.

    This workflow emits events to Vellum's infrastructure for monitoring
    when running externally. All workflow and node events will be sent
    to Vellum for visualization in the timeline view.

    Usage:
        # Set VELLUM_API_KEY environment variable
        workflow = BasicVellumEmitterWorkflow()
        result = workflow.run()

        # Events will appear in Vellum's monitoring UI
    """

    graph = StartNode >> NextNode
    emitters = [VellumEmitter()]

    class Outputs(BaseOutputs):
        final_value = NextNode.Outputs.final_value


class CustomVellumEmitterWorkflow(BaseWorkflow[BaseInputs, State]):
    """
    Workflow demonstrating custom VellumEmitter configuration.

    Shows how to configure VellumEmitter with custom settings for
    timeout, retries, and other options.
    """

    graph = StartNode >> NextNode

    # Custom VellumEmitter configuration
    emitters = [
        VellumEmitter(
            timeout=60.0,  # Custom timeout for API requests
            max_retries=5,  # More aggressive retry policy
        )
    ]

    class Outputs(BaseOutputs):
        final_value = NextNode.Outputs.final_value
