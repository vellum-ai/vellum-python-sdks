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
from ..nodes.advance_or_reject import AdvanceOrReject
from ..nodes.evaluate_resume import EvaluateResume
from ..nodes.extract_score import ExtractScore
from ..nodes.final_output_email_content import FinalOutputEmailContent
from ..nodes.write_next_round_email import WriteNextRoundEmail
from ..nodes.write_rejection_email import WriteRejectionEmail
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("d42056a1-cb01-4fd2-8eb7-560c9006511a"),
        entrypoint_node_source_handle_id=UUID("24241884-119a-4812-9d50-74b866b47fed"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=0, y=1329), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=53.2257811873921, y=-545.3742406253895, zoom=0.5924984837195854)
        ),
    )
    inputs_display = {
        Inputs.resume: WorkflowInputsDisplay(id=UUID("ce0a66eb-5882-4303-946b-75184270a926"), name="resume"),
        Inputs.job_requirements: WorkflowInputsDisplay(
            id=UUID("a6f1f373-6a17-43e2-baf4-aeb28d29318f"), name="job_requirements", color="cyan"
        ),
    }
    entrypoint_displays = {
        EvaluateResume: EntrypointDisplay(
            id=UUID("d42056a1-cb01-4fd2-8eb7-560c9006511a"),
            edge_display=EdgeDisplay(id=UUID("ee61d69d-35d0-43ea-987f-f08155b31c87")),
        )
    }
    edge_displays = {
        (AdvanceOrReject.Ports.branch_1, WriteNextRoundEmail): EdgeDisplay(
            id=UUID("31830773-663d-46da-accf-361fb6099657")
        ),
        (EvaluateResume.Ports.default, ExtractScore): EdgeDisplay(id=UUID("e1ed362b-1c3d-4227-888d-58253c59b706")),
        (ExtractScore.Ports.default, AdvanceOrReject): EdgeDisplay(id=UUID("986d385d-21a3-439b-ae5b-529819c3fac7")),
        (AdvanceOrReject.Ports.branch_2, WriteRejectionEmail): EdgeDisplay(
            id=UUID("0b53bbe8-c551-4ce2-90be-9ea82f35a136")
        ),
        (WriteNextRoundEmail.Ports.default, FinalOutputEmailContent): EdgeDisplay(
            id=UUID("04224ba0-dd18-4981-85d6-fdeb52d1c1cf")
        ),
        (WriteRejectionEmail.Ports.default, FinalOutputEmailContent): EdgeDisplay(
            id=UUID("dc3a45e5-3835-4ff8-b7b1-d18de8946c74")
        ),
    }
    output_displays = {
        Workflow.Outputs.email_copy: WorkflowOutputDisplay(
            id=UUID("84803d2a-ca83-40a3-b138-d8ebf64f8af1"), name="email_copy"
        )
    }
