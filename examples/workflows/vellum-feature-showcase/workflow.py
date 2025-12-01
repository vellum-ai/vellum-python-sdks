from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.combine_detailed_results import CombineDetailedResults
from .nodes.extract_subtopics_list import ExtractSubtopicsList
from .nodes.filter_subtopics import FilterSubtopics
from .nodes.generate_subtopics import GenerateSubtopics
from .nodes.map_detailed_exploration import MapDetailedExploration
from .nodes.simple_summary import SimpleSummary
from .nodes.subtopics_output import SubtopicsOutput
from .nodes.summary_output import SummaryOutput


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = (
        GenerateSubtopics
        >> ExtractSubtopicsList
        >> {
            FilterSubtopics.Ports.detailed
            >> MapDetailedExploration
            >> CombineDetailedResults
            >> {
                SummaryOutput,
                SubtopicsOutput,
            },
            FilterSubtopics.Ports.simple
            >> SimpleSummary
            >> {
                SummaryOutput,
                SubtopicsOutput,
            },
        }
    )

    class Outputs(BaseWorkflow.Outputs):
        subtopics = SubtopicsOutput.Outputs.value
        summary = SummaryOutput.Outputs.value
