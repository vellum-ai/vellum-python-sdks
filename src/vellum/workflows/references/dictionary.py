from typing import TYPE_CHECKING, Any, Dict, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState

_K = TypeVar("_K")
_V = TypeVar("_V")


class DictionaryReference(BaseDescriptor[Dict[_K, _V]]):
    def __init__(
        self,
        entries: Dict[_K, Union[BaseDescriptor[_V], _V]],
    ) -> None:
        self._entries = entries
        super().__init__(name=f"{{{', '.join(f'{k}: {v}' for k, v in entries.items())}}}", types=(dict,))

    def resolve(self, state: "BaseState") -> Dict[_K, _V]:
        # Imported here to avoid circular import with references/__init__.py
        from vellum.workflows.descriptors.utils import resolve_value

        return {key: resolve_value(value, state) for key, value in self._entries.items()}

    def __vellum_encode__(self) -> Dict[str, Any]:
        return {"type": "DICTIONARY_REFERENCE", "entries": self._entries}
