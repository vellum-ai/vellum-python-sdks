from uuid import UUID

from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    WorkflowDisplayData,
    WorkflowDisplayDataViewport,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.editor import NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

from ..inputs import Inputs
from ..nodes.add_agent_message_to_chat_history import AddAgentMessageToChatHistory
from ..nodes.add_evaluator_message_to_chat_history import AddEvaluatorMessageToChatHistory
from ..nodes.error_node import ErrorNode
from ..nodes.evaluator_agent import EvaluatorAgent
from ..nodes.extract_status import ExtractStatus
from ..nodes.final_output import FinalOutput
from ..nodes.needs_revision import NeedsRevision
from ..nodes.problem_solver_agent import ProblemSolverAgent
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("f30a644b-8dc2-44a6-889c-7fc68ee56faa"),
        entrypoint_node_source_handle_id=UUID("983050f4-430e-4456-87ad-65558edcbaa3"),
        entrypoint_node_display=NodeDisplayData(
            position=NodeDisplayPosition(x=1081.231395972988, y=460.252127819204), width=124, height=48
        ),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-1129.721988599967, y=74.55327214916164, zoom=0.6862790178657792)
        ),
    )
    inputs_display = {
        Inputs.math_problem: WorkflowInputsDisplay(id=UUID("e1819ef5-3ed2-4c9b-b8d5-bb6d3d572002"), name="math_problem")
    }
    entrypoint_displays = {
        ProblemSolverAgent: EntrypointDisplay(
            id=UUID("f30a644b-8dc2-44a6-889c-7fc68ee56faa"),
            edge_display=EdgeDisplay(id=UUID("d8573de7-4888-4caa-9dd9-2ed6135f846f")),
        )
    }
    edge_displays = {
        (EvaluatorAgent.Ports.default, ExtractStatus): EdgeDisplay(id=UUID("a960b800-472f-4298-9434-d62471a50c68")),
        (ExtractStatus.Ports.default, NeedsRevision): EdgeDisplay(id=UUID("32de57b3-bee0-4de2-8bce-1aab36505522")),
        (NeedsRevision.Ports.branch_1, FinalOutput): EdgeDisplay(id=UUID("454cc03e-7570-4700-971d-5b2133a303b9")),
        (NeedsRevision.Ports.branch_3, ErrorNode): EdgeDisplay(id=UUID("07d12270-0571-4116-b0df-785ed8a9f7f8")),
        (ProblemSolverAgent.Ports.default, AddAgentMessageToChatHistory): EdgeDisplay(
            id=UUID("e78b21fc-8618-4f9a-b138-96998fac77a3")
        ),
        (AddAgentMessageToChatHistory.Ports.default, EvaluatorAgent): EdgeDisplay(
            id=UUID("c75940f1-fcc0-4659-b5e9-d231dcb6cec2")
        ),
        (NeedsRevision.Ports.branch_2, AddEvaluatorMessageToChatHistory): EdgeDisplay(
            id=UUID("8576ea61-980b-4391-8685-143fe191ccf7")
        ),
        (AddEvaluatorMessageToChatHistory.Ports.default, ProblemSolverAgent): EdgeDisplay(
            id=UUID("00cc66f2-5823-44a1-b88c-82a771211ade")
        ),
    }
    output_displays = {
        Workflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("d864d797-940c-44c1-a59d-a014ce5b9551"), name="final-output"
        )
    }
