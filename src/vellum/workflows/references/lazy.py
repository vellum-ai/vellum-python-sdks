import ast
import inspect
from typing import TYPE_CHECKING, Callable, Generic, TypeVar, Union, get_args

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class LazyReference(BaseDescriptor[_T], Generic[_T]):
    def __init__(
        self,
        get: Union[Callable[[], BaseDescriptor[_T]], str],
    ) -> None:
        self._get = get
        # TODO: figure out this some times returns empty
        # Original example: https://github.com/vellum-ai/workflows-as-code-runner-prototype/pull/128/files#diff-67aaa468aa37b6130756bfaf93f03954d7b518617922efb3350882ea4ae03d60R36 # noqa: E501
        # https://app.shortcut.com/vellum/story/4993
        types = get_args(type(self))
        super().__init__(name=self._get_name(), types=types)

    def resolve(self, state: "BaseState") -> _T:
        from vellum.workflows.descriptors.utils import resolve_value

        if isinstance(self._get, str):
            # The full solution will involve creating a nodes registry on `WorkflowContext`. I want to update
            # how WorkflowContext works so that we could just access it directly instead of it needing to be
            # passed in, similar to get_workflow_context(). Because we don't want this to slow down p1 issues
            # that we are debugging with existing workflows, using the following workaround for now.
            for output_reference, value in state.meta.node_outputs.items():
                if str(output_reference) == self._get:
                    return value

            # Fix typing surrounding the return value of node outputs/output descriptors
            # https://app.shortcut.com/vellum/story/4783
            return undefined  # type: ignore[return-value]

        return resolve_value(self._get(), state)

    def _get_name(self) -> str:
        """
        We try our best to parse out the source code that generates the descriptor,
        setting that as the descriptor's name. Names are only used for debugging, so
        we could flesh out edge cases over time.
        """
        if isinstance(self._get, str):
            return self._get

        source = inspect.getsource(self._get).strip()
        try:
            parsed = ast.parse(source)
            assignment = parsed.body[0]

            if not isinstance(assignment, ast.Assign):
                return source

            call = assignment.value
            if not isinstance(call, ast.Call) or not call.args:
                return source

            lambda_expression = call.args[0]
            if not isinstance(lambda_expression, ast.Lambda):
                return source

            body = lambda_expression.body
            return source[body.col_offset : body.end_col_offset]
        except Exception:
            return source
