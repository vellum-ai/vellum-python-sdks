from uuid import UUID

from vellum_ee.workflows.display.editor import NodeDisplayComment, NodeDisplayData, NodeDisplayPosition
from vellum_ee.workflows.display.nodes import BaseInlinePromptNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplayOverrides

from ...nodes.problem_solver_agent import ProblemSolverAgent


class ProblemSolverAgentDisplay(BaseInlinePromptNodeDisplay[ProblemSolverAgent]):
    label = "Problem Solver Agent"
    node_id = UUID("89e3e279-0cec-4356-8308-5e7076dbd52e")
    output_id = UUID("c5b21544-5cd2-4df7-9826-74cdf558354f")
    array_output_id = UUID("bbd6be27-5b0f-4d54-9a31-0e12efeb92aa")
    target_handle_id = UUID("b9fba906-f169-4ca3-8edc-28f363db3eb8")
    node_input_ids_by_name = {
        "prompt_inputs.math_problem": UUID("1b144a04-d5d1-4b03-8314-ee13b515324c"),
        "prompt_inputs.chat_history": UUID("122598c5-bcf4-437b-988a-7c6d76151c4c"),
    }
    attribute_ids_by_name = {"ml_model": UUID("4681a133-2a9b-4ffc-8e69-2fa80f227766")}
    output_display = {
        ProblemSolverAgent.Outputs.text: NodeOutputDisplay(
            id=UUID("c5b21544-5cd2-4df7-9826-74cdf558354f"), name="text"
        ),
        ProblemSolverAgent.Outputs.results: NodeOutputDisplay(
            id=UUID("bbd6be27-5b0f-4d54-9a31-0e12efeb92aa"), name="results"
        ),
        ProblemSolverAgent.Outputs.json: NodeOutputDisplay(
            id=UUID("abfe5576-ea3e-47ca-b554-1865b9f10823"), name="json"
        ),
    }
    port_displays = {
        ProblemSolverAgent.Ports.default: PortDisplayOverrides(id=UUID("5aa4790e-6eab-4adb-8f77-89df21e32a0e"))
    }
    display_data = NodeDisplayData(
        position=NodeDisplayPosition(x=1473.2938896047522, y=303.5007601991737),
        width=480,
        height=315,
        comment=NodeDisplayComment(expanded=True),
    )
