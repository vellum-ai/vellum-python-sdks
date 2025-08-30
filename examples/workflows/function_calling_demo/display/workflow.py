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
from ..nodes.accumulate_chat_history import AccumulateChatHistory
from ..nodes.conditional_node import ConditionalNode
from ..nodes.conditional_node_10 import ConditionalNode10
from ..nodes.error_node import ErrorNode
from ..nodes.final_accumulation_of_chat_history import FinalAccumulationOfChatHistory
from ..nodes.final_output import FinalOutput
from ..nodes.get_current_weather import GetCurrentWeather
from ..nodes.output_type import OutputType
from ..nodes.parse_function_call import ParseFunctionCall
from ..nodes.prompt_node import PromptNode
from ..workflow import FunctionCallingDemoWorkflow


class FunctionCallingDemoWorkflowDisplay(BaseWorkflowDisplay[FunctionCallingDemoWorkflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("8d9848b6-37f1-433d-9eb9-d85788007e8b"),
        entrypoint_node_source_handle_id=UUID("39eb234b-7594-4855-9cb8-dfcaff48963c"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=165, y=315), width=124, height=48),
        display_data=WorkflowDisplayData(
            viewport=WorkflowDisplayDataViewport(x=-730.0959027261842, y=128.0011183508181, zoom=0.49585442352220244)
        ),
    )
    inputs_display = {
        Inputs.chat_history: WorkflowInputsDisplay(id=UUID("b120c597-1e61-4779-b8d1-34676f9ecabc"), name="chat_history")
    }
    entrypoint_displays = {
        PromptNode: EntrypointDisplay(
            id=UUID("8d9848b6-37f1-433d-9eb9-d85788007e8b"),
            edge_display=EdgeDisplay(id=UUID("894bb47f-c560-463a-8516-1f1dd9a45463")),
        )
    }
    edge_displays = {
        (ParseFunctionCall.Ports.default, ConditionalNode): EdgeDisplay(
            id=UUID("413c943d-3aa0-459e-971d-ff89a286108f")
        ),
        (ConditionalNode.Ports.branch_1, GetCurrentWeather): EdgeDisplay(
            id=UUID("ce18995e-2f1e-481e-bcf0-bfa1e9d6db8e")
        ),
        (GetCurrentWeather.Ports.default, AccumulateChatHistory): EdgeDisplay(
            id=UUID("1efde279-9cd7-4917-b508-bb57768bd5e6")
        ),
        (AccumulateChatHistory.Ports.default, PromptNode): EdgeDisplay(id=UUID("7fd1861c-0b94-4e14-a724-88a5a67b8b02")),
        (PromptNode.Ports.default, OutputType): EdgeDisplay(id=UUID("76dfcf8c-ccd0-4142-83de-f63662af6474")),
        (OutputType.Ports.default, ConditionalNode10): EdgeDisplay(id=UUID("20afd4d8-bf0c-402b-a5ec-d231ed819e92")),
        (ConditionalNode10.Ports.branch_1, ParseFunctionCall): EdgeDisplay(
            id=UUID("b7cade05-cec8-459f-8113-e334a8f761f5")
        ),
        (ConditionalNode.Ports.branch_2, ErrorNode): EdgeDisplay(id=UUID("b5adfbdd-38f2-4377-8eee-d539f7747c26")),
        (ConditionalNode10.Ports.branch_2, FinalAccumulationOfChatHistory): EdgeDisplay(
            id=UUID("588faf16-b4b9-45f4-bdd1-b18926f6c5e5")
        ),
        (FinalAccumulationOfChatHistory.Ports.default, FinalOutput): EdgeDisplay(
            id=UUID("988f4094-ec68-4123-b0ca-2990e973dce9")
        ),
    }
    output_displays = {
        FunctionCallingDemoWorkflow.Outputs.final_output: WorkflowOutputDisplay(
            id=UUID("e869f551-b02c-465f-90b3-ad2021b3c618"), name="final-output"
        )
    }
