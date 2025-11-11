from vellum.workflows import BaseWorkflow

from .nodes.output import Output
from .triggers.scheduled import Scheduled


class Workflow(BaseWorkflow):
    # TODO: Uncomment trigger test once we fix mypy issue with graph: https://linear.app/vellum/issue/APO-2127/fix-mypy-issue-of-graph-types
    graph = {  # type: ignore[assignment]
        Output,
        Scheduled >> Output,
    }

    class Outputs(BaseWorkflow.Outputs):
        output = Output.Outputs.value
