from vellum.workflows.nodes.displayable import GuardrailNode as BaseGuardrailNode

from ..inputs import Inputs


class GuardrailNode(BaseGuardrailNode):
    metric_definition = "589df5bd-8c0d-4797-9a84-9598ecd043de"
    metric_inputs = {
        "expected": Inputs.expected,
        "actual": Inputs.actual,
    }
    release_tag = "LATEST"
