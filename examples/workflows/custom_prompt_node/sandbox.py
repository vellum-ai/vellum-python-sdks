from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import CustomPromptNodeWorkflow

if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")


workflow = CustomPromptNodeWorkflow()
runner = WorkflowSandboxRunner(workflow, inputs=[Inputs(message="It's such a beautiful day today!")])
runner.run()
