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
from ..nodes.conditional_router import ConditionalRouter
from ..nodes.echo_request import EchoRequest
from ..nodes.error_node import ErrorNode
from ..nodes.exit_node import ExitNode
from ..nodes.fibonacci import Fibonacci
from ..nodes.get_temperature import GetTemperature
from ..nodes.my_prompt import MyPrompt
from ..workflow import CustomBaseNodeWorkflow


class CustomBaseNodeWorkflowDisplay(BaseWorkflowDisplay[CustomBaseNodeWorkflow]):
    workflow_display = WorkflowMetaDisplay(
        entrypoint_node_id=UUID("5aa611bd-83d6-4a34-b2f4-3b3511c56998"),
        entrypoint_node_source_handle_id=UUID("213ccd7a-bd48-45a3-8387-af9afa946e0e"),
        entrypoint_node_display=NodeDisplayData(position=NodeDisplayPosition(x=0, y=0), width=None, height=None),
        display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=0, y=0, zoom=1)),
    )
    inputs_display = {
        Inputs.query: WorkflowInputsDisplay(id=UUID("a6cc5f97-122f-4d54-b70a-43874e2c6573"), name="query")
    }
    entrypoint_displays = {
        MyPrompt: EntrypointDisplay(
            id=UUID("5aa611bd-83d6-4a34-b2f4-3b3511c56998"),
            edge_display=EdgeDisplay(id=UUID("8f376c53-b70a-4c09-a187-27fe25b306bc")),
        )
    }
    edge_displays = {
        (MyPrompt.Ports.default, ConditionalRouter): EdgeDisplay(id=UUID("af748cf1-8aab-4cfc-b73d-141a4a506d40")),
        (ConditionalRouter.Ports.echo_request, EchoRequest): EdgeDisplay(
            id=UUID("47e23829-7b60-4303-b242-64c1ff299e39")
        ),
        (EchoRequest.Ports.default, MyPrompt): EdgeDisplay(id=UUID("5a78572f-595e-4fe2-acc5-e45540d2b98b")),
        (ConditionalRouter.Ports.exit, ExitNode): EdgeDisplay(id=UUID("1a518848-89f6-4036-9f0b-6e1c09b4a8a7")),
        (ConditionalRouter.Ports.get_temperature, GetTemperature): EdgeDisplay(
            id=UUID("f8297a07-5d2e-45a0-8610-780b6307c9d5")
        ),
        (GetTemperature.Ports.default, MyPrompt): EdgeDisplay(id=UUID("93ddfe51-7ce3-46f4-8c60-0ea2fe2e228e")),
        (ConditionalRouter.Ports.fibonacci, Fibonacci): EdgeDisplay(id=UUID("038eb1b3-663a-49b5-9c0c-e4f6afef8d46")),
        (Fibonacci.Ports.default, MyPrompt): EdgeDisplay(id=UUID("1ea51ea2-a74f-4638-88df-496183fc1014")),
        (ConditionalRouter.Ports.unknown, ErrorNode): EdgeDisplay(id=UUID("414653b1-f3a6-40da-9973-5a5bda741c85")),
    }
    output_displays = {
        CustomBaseNodeWorkflow.Outputs.answer: WorkflowOutputDisplay(
            id=UUID("708005f3-81e0-4886-95e9-ccb0d6c029d3"), name="answer"
        )
    }
