from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .evaluate_resume import EvaluateResume


class ExtractScore(TemplatingNode[BaseState, str]):
    template = """{{- resume_score_json[\"recommendation\"] -}}"""
    inputs = {
        "resume_score_json": EvaluateResume.Outputs.json,
    }
