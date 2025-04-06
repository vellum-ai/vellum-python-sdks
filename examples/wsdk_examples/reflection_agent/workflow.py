from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.add_agent_message_to_chat_history import AddAgentMessageToChatHistory
from .nodes.add_evaluator_message_to_chat_history import AddEvaluatorMessageToChatHistory
from .nodes.error_node import ErrorNode
from .nodes.evaluator_agent import EvaluatorAgent
from .nodes.extract_status import ExtractStatus
from .nodes.final_output import FinalOutput
from .nodes.needs_revision import NeedsRevision
from .nodes.note import Note
from .nodes.problem_solver_agent import ProblemSolverAgent


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = (
        ProblemSolverAgent
        >> AddAgentMessageToChatHistory
        >> EvaluatorAgent
        >> ExtractStatus
        >> {
            NeedsRevision.Ports.branch_1 >> FinalOutput,
            NeedsRevision.Ports.branch_3 >> ErrorNode,
            NeedsRevision.Ports.branch_2 >> AddEvaluatorMessageToChatHistory >> ProblemSolverAgent,
        }
    )
    unused_graphs = {Note}

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
