from typing import TYPE_CHECKING, Any, Type, Union

from vellum.workflows.constants import undefined
from vellum.workflows.types.generics import is_workflow_class

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState


def resolve_output_reference_by_string(ref_string: str, state: "BaseState") -> Union[Any, Type[undefined]]:
    """
    Resolves an output reference by its string representation.

    Checks both node outputs and workflow outputs to find a matching reference.

    Args:
        ref_string: The string representation of the output reference (e.g., "MyNode.Outputs.response")
        state: The workflow state to resolve against

    Returns:
        The resolved value if found, otherwise undefined
    """
    from vellum.workflows.descriptors.utils import resolve_value

    # Check node outputs first
    for output_reference, value in state.meta.node_outputs.items():
        if str(output_reference) == ref_string:
            return value

    # Check workflow outputs
    workflow_definition = state.meta.workflow_definition
    if is_workflow_class(workflow_definition):
        for output_reference in workflow_definition.Outputs:
            if str(output_reference) == ref_string:
                return resolve_value(output_reference.instance, state)

    return undefined
