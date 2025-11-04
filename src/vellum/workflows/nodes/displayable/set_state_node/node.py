from typing import Any, ClassVar, Dict, Generic

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.generics import StateType


class SetStateNode(BaseNode[StateType], Generic[StateType]):
    """
    A node that sets multiple state values at once.

    This node accepts a dictionary mapping state paths to values and sets them all.
    Values can be actual values or descriptors.

    Example:
        operations = {
            "chat_history": State.chat_history.concat(LazyReference("MyAgentNode.Outputs.chat_history")),
            "counter": State.counter + 1,
            "total_tokens": State.user_tokens.add(State.assistant_tokens)
        }

    Args:
        operations: Dictionary mapping state attribute names to values (descriptors or actual values)
    """

    __legacy_id__ = True

    # Dictionary mapping state paths to values
    operations: ClassVar[Dict[str, Any]] = {}

    class Outputs(BaseOutputs):
        """
        The outputs of the SetStateNode.

        result: Dict[str, Any] - Dictionary of all state updates
        """

        result: Dict[str, Any]

    def run(self) -> Outputs:
        """
        Run the node and set all the state values.
        Resolves descriptors to their actual values before setting state.
        """
        # First pass: validate and resolve all operations without mutating state
        resolved_updates: Dict[str, Any] = {}
        for path, value in self.operations.items():
            # Validate the state attribute exists prior to any mutation
            if not hasattr(self.state, path):
                raise NodeException(
                    f"State does not have attribute '{path}'. "
                    f"Only existing state attributes can be set via SetStateNode.",
                    code=WorkflowErrorCode.INVALID_STATE,
                )

            # Resolve the value if it's a descriptor against the current (unmodified) state
            if isinstance(value, BaseDescriptor):
                resolved_value = resolve_value(value, self.state)
            else:
                resolved_value = value

            resolved_updates[path] = resolved_value

        # Second pass: apply the resolved updates to the state atomically
        with self.state.__atomic__():
            for path, resolved_value in resolved_updates.items():
                setattr(self.state, path, resolved_value)

        return self.Outputs(result=resolved_updates)
