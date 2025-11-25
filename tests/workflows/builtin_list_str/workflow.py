from vellum.workflows import BaseWorkflow

from .nodes.raw_code import RawCode
from .nodes.the_end import TheEnd


class Workflow(BaseWorkflow):
    graph = RawCode >> TheEnd

    class Outputs(BaseWorkflow.Outputs):
        the_end = TheEnd.Outputs.value
