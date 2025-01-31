from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.retry_node import RetryNode


@RetryNode.wrap(max_attempts=3, delay=0.1)
class RetryableNode(BaseNode):
    attempt_number = RetryNode.SubworkflowInputs.attempt_number

    class Outputs(BaseNode.Outputs):
        execution_count: int

    def run(self) -> Outputs:
        if self.attempt_number < 3:
            raise Exception("This is a retryable node")

        return self.Outputs(execution_count=self.attempt_number)


class SimpleRetryExample(BaseWorkflow):
    graph = RetryableNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = RetryableNode.Outputs.execution_count
