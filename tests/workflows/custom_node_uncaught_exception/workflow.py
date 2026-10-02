from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class CustomNodeWithUncaughtException(BaseNode):
    """
    A custom node that throws an uncaught exception (AttributeError).
    This simulates the scenario from the Linear ticket APO-2674 where
    a custom node throws an exception that is not caught.
    """

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        items = ["apple", "banana", "cherry"]
        for item in items:
            item.get("title")  # This will fail - strings don't have .get() method
        return self.Outputs(result="success")


class CustomNodeUncaughtExceptionWorkflow(BaseWorkflow):
    """
    A workflow that demonstrates a custom node that throws an uncaught exception.
    The exception should be captured with a full stack trace.
    """

    graph = CustomNodeWithUncaughtException
