from uuid import UUID

from vellum_ee.workflows.display.nodes import BaseFinalOutputNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeInputDisplay, NodeOutputDisplay
from vellum_ee.workflows.display.vellum import (
    BinaryWorkflowExpression,
    LogicalOperator,
    NodeDisplayData,
    NodeDisplayPosition,
    NodeOutputWorkflowReference,
)

from ...nodes.final_output_2 import FinalOutput2


class FinalOutput2Display(BaseFinalOutputNodeDisplay[FinalOutput2]):
    label = "Final Output 2"
    node_id = UUID("f9c5254c-b86d-420d-811a-a1674df273cd")
    target_handle_id = UUID("87d73dc6-cafd-4f8b-b2fd-8367baba5d61")
    output_id = UUID("8c6e5464-8916-4039-b911-cf707855d372")
    output_name = "answer"
    node_input_id = UUID("4a999b21-0555-404c-a4f4-c613cd108450")
    node_input_display = NodeInputDisplay(
        id=UUID("8c6e5464-8916-4039-b911-cf707855d372"),
        name="node_input",
        type="STRING",
        value=BinaryWorkflowExpression(
            lhs=BinaryWorkflowExpression(
                lhs=BinaryWorkflowExpression(
                    lhs=NodeOutputWorkflowReference(
                        node_id="58e6c822-2d0d-4e81-9a00-0046a02741d4",
                        node_output_id="e9c9ddb8-4057-4755-bbbd-6ca0291aac9a",
                    ),
                    rhs=NodeOutputWorkflowReference(
                        node_id="3f4ce7b7-8389-42e1-abab-a7afe9a142b5",
                        node_output_id="8e2d57c3-85a3-4acb-b4d3-998c6906e389",
                    ),
                    operator=LogicalOperator.COALESCE,
                ),
                rhs=NodeOutputWorkflowReference(
                    node_id="9722b9da-0164-40fb-9270-a0fc9b87b1f9",
                    node_output_id="df6d8990-e05b-45e1-9294-ccf58252757b",
                ),
                operator=LogicalOperator.COALESCE,
            ),
            rhs=NodeOutputWorkflowReference(
                node_id="235b2e34-c6a3-48aa-b2cc-090571b41ea8", node_output_id="7b1ca9d1-d829-4329-b9f3-a864c3ce4230"
            ),
            operator=LogicalOperator.COALESCE,
        ),
    )
    node_input_ids_by_name = {"node_input": UUID("4a999b21-0555-404c-a4f4-c613cd108450")}
    output_display = {
        FinalOutput2.Outputs.value: NodeOutputDisplay(id=UUID("8c6e5464-8916-4039-b911-cf707855d372"), name="value")
    }
    display_data = NodeDisplayData(position=NodeDisplayPosition(x=5134, y=443), width=480, height=271)
