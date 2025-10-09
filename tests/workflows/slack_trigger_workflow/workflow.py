from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.slack import SlackTrigger

from .nodes.process_message import ProcessMessageNode


class SlackTriggerWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Example workflow triggered by Slack events."""

    graph = SlackTrigger >> ProcessMessageNode

    class Outputs(BaseWorkflow.Outputs):
        result = ProcessMessageNode.Outputs.processed_message
