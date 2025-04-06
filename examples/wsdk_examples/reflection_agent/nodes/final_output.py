from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .problem_solver_agent import ProblemSolverAgent


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = ProblemSolverAgent.Outputs.text
