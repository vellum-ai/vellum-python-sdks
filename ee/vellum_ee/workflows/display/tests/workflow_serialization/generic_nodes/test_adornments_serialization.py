from uuid import uuid4

from deepdiff import DeepDiff

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.vellum.base_node import BaseNodeDisplay

from ee.vellum_ee.workflows.display.base import WorkflowInputsDisplay


class Inputs(BaseInputs):
    input: str


@RetryNode.wrap(max_attempts=3)
class InnerRetryGenericNode(BaseNode):
    input = Inputs.input

    class Outputs(BaseOutputs):
        output: str


class InnerRetryGenericNodeDisplay(BaseNodeDisplay[InnerRetryGenericNode.__wrapped_node__]):
    pass


class OuterRetryNodeDisplay(BaseNodeDisplay[InnerRetryGenericNode]):
    pass


class InnerRetryGenericNodeWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    graph = {InnerRetryGenericNode}


def test_serialize_node__retry(serialize_node):
    input_id = uuid4()
    serialized_node = serialize_node(
        node_class=InnerRetryGenericNode,
        global_workflow_input_displays={Inputs.input: WorkflowInputsDisplay(id=input_id)},
    )
    assert not DeepDiff(
        {},
        serialized_node,
        ignore_order=True,
    )
