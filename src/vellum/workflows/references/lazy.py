import ast
import inspect
import logging
from typing import TYPE_CHECKING, Callable, Generic, TypeVar, Union, get_args

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")

logger = logging.getLogger(__name__)


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
            # We are comparing Output string references - when if we want to be exact,
            # should be comparing the Output class themselves
            for output_reference, value in state.meta.node_outputs.items():
                if str(output_reference) == self._get:
                    return value

            child_reference = self.resolve(state.meta.parent) if state.meta.parent else None

            # Fix typing surrounding the return value of node outputs/output descriptors
            # https://app.shortcut.com/vellum/story/4783
            return child_reference or undefined  # type: ignore[return-value]

        return resolve_value(self._get(), state)

    def _get_name(self) -> str:
        """
        We try our best to parse out the source code that generates the descriptor,
        setting that as the descriptor's name. Names are only used for debugging, so
        we could flesh out edge cases over time.
        """
        if isinstance(self._get, str):
            return self._get

        try:
            source = inspect.getsource(self._get).strip()
        except Exception:
            logger.exception("Error getting source for lazy reference")
            return self._get.__name__

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
