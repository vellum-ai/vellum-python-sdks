from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.state import BaseState
from vellum.workflows.triggers import SlackTrigger

from .nodes.check_tag_node import CheckTagNode
from .nodes.create_linear_ticket_node import CreateLinearTicketNode
from .nodes.final_output import FinalOutput
from .nodes.output_linear_ticket import OutputLinearTicket
from .nodes.output_path_taken import OutputPathTaken
from .nodes.reply_in_slack_node import ReplyInSlackNode


class Workflow(BaseWorkflow[BaseInputs, BaseState]):
    graph = SlackTrigger >> {
        CheckTagNode.Ports.tagged >> CreateLinearTicketNode >> ReplyInSlackNode >> OutputLinearTicket,
        CheckTagNode.Ports.not_tagged >> OutputPathTaken >> FinalOutput,
    }

    class Outputs(BaseWorkflow.Outputs):
        path_taken = FinalOutput.Outputs.value
        linear_ticket = OutputLinearTicket.Outputs.value
