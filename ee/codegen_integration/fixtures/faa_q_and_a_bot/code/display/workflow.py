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
from ..nodes.api_node import APINode
from ..nodes.conditional_node import ConditionalNode
from ..nodes.faa_document_store import FAADocumentStore
from ..nodes.final_output_2 import FinalOutput2
from ..nodes.formatted_search_results import FormattedSearchResults
from ..nodes.most_recent_message import MostRecentMessage
from ..nodes.prompt_node import PromptNode
from ..nodes.prompt_node_14 import PromptNode14
from ..nodes.prompt_node_16 import PromptNode16
from ..nodes.prompt_node_18 import PromptNode18
from ..nodes.prompt_node_19 import PromptNode19
from ..nodes.prompt_node_9 import PromptNode9
from ..nodes.subworkflow_node import SubworkflowNode
from ..nodes.templating_node import TemplatingNode
from ..nodes.templating_node_15 import TemplatingNode15
from ..workflow import Workflow


class WorkflowDisplay(BaseWorkflowDisplay[Workflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("81ec43d2-49ec-47ce-b953-faaec3a22c63"),
        entrypoint_node_source_handle_id=UUID("6888c8eb-9dba-42b4-94d4-52900edcfeea"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=0, y=388.75), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-3043.2099511931765, y=-458.8278903628302, zoom=0.9343894537129058)
        ),
    )
    inputs_display = {
        Inputs.chat_history: WorkflowInputsDisplay(id=UUID("d4663e15-8871-42d8-8ef7-59baff2cd436"), name="chat_history")
    }
    entrypoint_displays = {
        MostRecentMessage: EntrypointDisplay(
            id=UUID("81ec43d2-49ec-47ce-b953-faaec3a22c63"),
            edge_display=EdgeDisplay(id=UUID("2ea073be-8a97-431d-8878-27309f0ac8c0")),
        )
    }
    edge_displays = {
        (MostRecentMessage.Ports.default, PromptNode): EdgeDisplay(
            id=UUID("7ad283cf-0316-48f0-bc39-10ab3623ec7f"), z_index=None
        ),
        (PromptNode.Ports.default, TemplatingNode): EdgeDisplay(
            id=UUID("196807e4-b1f7-4286-b02b-5caf837f0362"), z_index=None
        ),
        (TemplatingNode.Ports.default, ConditionalNode): EdgeDisplay(
            id=UUID("293a13ac-89c5-4fc6-a142-dd9a5e36d730"), z_index=None
        ),
        (ConditionalNode.Ports.branch_3, FAADocumentStore): EdgeDisplay(
            id=UUID("2091a647-7342-4657-a713-55b34148862d"), z_index=None
        ),
        (FAADocumentStore.Ports.default, FormattedSearchResults): EdgeDisplay(
            id=UUID("9713f09b-7515-459c-9681-2e72cc59cc81"), z_index=None
        ),
        (FormattedSearchResults.Ports.default, PromptNode9): EdgeDisplay(
            id=UUID("bde304f6-a485-4e87-836a-6dcb897ed38a"), z_index=None
        ),
        (ConditionalNode.Ports.branch_2, PromptNode16): EdgeDisplay(
            id=UUID("a90e7c00-ee9a-41d4-8339-f4bdd6b747b8"), z_index=None
        ),
        (PromptNode16.Ports.default, TemplatingNode15): EdgeDisplay(
            id=UUID("094fccc2-855c-456e-a1db-0df57cd583c1"), z_index=None
        ),
        (TemplatingNode15.Ports.default, APINode): EdgeDisplay(
            id=UUID("02b212d8-d6cc-4e02-99ea-dce5716cb73b"), z_index=None
        ),
        (APINode.Ports.default, PromptNode18): EdgeDisplay(
            id=UUID("1e4489fd-62ee-4b2d-8abb-b3082485ef01"), z_index=None
        ),
        (ConditionalNode.Ports.branch_4, PromptNode19): EdgeDisplay(
            id=UUID("a5d7013a-4ecb-4f35-8230-ef8fbfecda27"), z_index=None
        ),
        (ConditionalNode.Ports.branch_1, SubworkflowNode): EdgeDisplay(
            id=UUID("7e517fcd-b174-435f-b429-39a5230571b8"), z_index=None
        ),
        (SubworkflowNode.Ports.default, PromptNode14): EdgeDisplay(
            id=UUID("84229185-fb0e-4f7f-bd11-1de423396872"), z_index=None
        ),
        (PromptNode19.Ports.default, FinalOutput2): EdgeDisplay(
            id=UUID("f88c3cad-c845-41af-abe6-118e0606ac16"), z_index=None
        ),
        (PromptNode18.Ports.default, FinalOutput2): EdgeDisplay(
            id=UUID("87051c37-8d28-4849-9c09-e6d243b744b6"), z_index=None
        ),
        (PromptNode9.Ports.default, FinalOutput2): EdgeDisplay(
            id=UUID("9e19ee9e-24a6-47e7-8b10-44781a53018f"), z_index=None
        ),
        (PromptNode14.Ports.default, FinalOutput2): EdgeDisplay(
            id=UUID("417f05e4-f73a-4d93-98ab-ada609062d38"), z_index=None
        ),
    }
    output_displays = {
        Workflow.Outputs.answer: WorkflowOutputDisplay(id=UUID("8c6e5464-8916-4039-b911-cf707855d372"), name="answer")
    }
