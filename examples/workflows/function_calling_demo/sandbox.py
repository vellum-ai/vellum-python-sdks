from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import ChatMessage, Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


workflow = Workflow()
runner = WorkflowSandboxRunner(
    workflow,
    inputs=[
        Inputs(
            chat_history=[
                ChatMessage(
                    role="USER",
                    text="What is the weather in San Francisco?",
                )
            ]
        )
    ],
)
runner.run()
