from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


runner = WorkflowSandboxRunner(
    workflow=Workflow(),
    inputs=[
        Inputs(
            math_problem="A cyclist travels uphill at an average speed of 8 mph and downhill along the same route at an average speed of 24 mph. If the total round-trip takes 4 hours, what is the total distance traveled?\n"
        ),
    ],
)

runner.run()
