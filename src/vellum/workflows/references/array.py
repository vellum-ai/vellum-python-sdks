from typing import TYPE_CHECKING, Any, Dict, List, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class ArrayReference(BaseDescriptor[List[_T]]):
    def __init__(
        self,
        items: List[Union[BaseDescriptor[_T], _T]],
    ) -> None:
        self._items = items
        super().__init__(name=f"[{', '.join(str(item) for item in items)}]", types=(list,))

    def resolve(self, state: "BaseState") -> List[_T]:
        # Imported here to avoid circular import with references/__init__.py
        from vellum.workflows.descriptors.utils import resolve_value

        return [resolve_value(item, state) for item in self._items]

    def __vellum_encode__(self) -> Dict[str, Any]:
        return {"type": "ARRAY_REFERENCE", "items": self._items}
