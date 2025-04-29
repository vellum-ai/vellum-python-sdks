from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.advance_or_reject import AdvanceOrReject
from .nodes.evaluate_resume import EvaluateResume
from .nodes.extract_score import ExtractScore
from .nodes.final_output_email_content import FinalOutputEmailContent
from .nodes.write_next_round_email import WriteNextRoundEmail
from .nodes.write_rejection_email import WriteRejectionEmail


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = (
        EvaluateResume
        >> ExtractScore
        >> {
            AdvanceOrReject.Ports.branch_1 >> WriteNextRoundEmail,
            AdvanceOrReject.Ports.branch_2 >> WriteRejectionEmail,
        }
        >> FinalOutputEmailContent
    )

    class Outputs(BaseWorkflow.Outputs):
        email_copy = FinalOutputEmailContent.Outputs.value
