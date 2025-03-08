from queue import Queue
from typing import TYPE_CHECKING, Any, Generator, Generic, Optional, Tuple, Type, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.outputs import BaseOutputs
    from vellum.workflows.state.base import BaseState


_OutputType = TypeVar("_OutputType")


class OutputReference(BaseDescriptor[_OutputType], Generic[_OutputType]):
    def __init__(
        self,
        *,
        name: str,
        types: Tuple[Type[_OutputType], ...],
        instance: Optional[_OutputType],
        outputs_class: Type["BaseOutputs"],
    ) -> None:
        super().__init__(name=name, types=types, instance=instance)
        self._outputs_class = outputs_class

    @property
    def outputs_class(self) -> Type["BaseOutputs"]:
        return self._outputs_class

    def resolve(self, state: "BaseState") -> _OutputType:
        node_output = state.meta.node_outputs.get(self, undefined)
        if isinstance(node_output, Queue):
            # Fix typing surrounding the return value of node outputs
            # https://app.shortcut.com/vellum/story/4783
            return self._as_generator(node_output)  # type: ignore[return-value]

        if node_output is not undefined:
            return cast(_OutputType, node_output)

        if state.meta.parent:
            return self.resolve(state.meta.parent)

        # Fix typing surrounding the return value of node outputs
        # https://app.shortcut.com/vellum/story/4783
        return cast(Type[undefined], node_output)  # type: ignore[return-value]

    def _as_generator(self, node_output: Queue) -> Generator[_OutputType, None, Type[undefined]]:
        while True:
            item = node_output.get()
            if item is undefined:
                return undefined
            yield cast(_OutputType, item)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return super().__eq__(other) and self._outputs_class == other._outputs_class

    def __hash__(self) -> int:
        return hash((self._outputs_class, self._name))

    def __repr__(self) -> str:
        return f"{self._outputs_class.__qualname__}.{self.name}"

    def __deepcopy__(self, memo: dict) -> "OutputReference[_OutputType]":
        return OutputReference(
            name=self._name, types=self._types, instance=self._instance, outputs_class=self._outputs_class
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
