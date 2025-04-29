from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.data_extractor import DataExtractor
from .nodes.final_output import FinalOutput


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = DataExtractor >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
