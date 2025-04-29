from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


runner = WorkflowSandboxRunner(
    workflow=Workflow(),
    inputs=[
        Inputs(
            question="Hi! How do i pass inputs into an API node? I can do URL params (preferred) or JSON body, but I couldn't figure either out. "
        ),
        Inputs(question="Do you support Llama 9.12? Do you plan to soon? "),
    ],
)

runner.run()
