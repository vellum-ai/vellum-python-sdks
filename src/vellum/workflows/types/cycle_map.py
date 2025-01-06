from typing import Callable, Dict, Generic, List, TypeVar

_K = TypeVar("_K")
_T = TypeVar("_T")


class CycleMap(Generic[_K, _T]):
    """
    A map that cycles through a list of items for each key.
    """

    def __init__(self, items: List[_T], key_by: Callable[[_T], _K]):
        self._items: Dict[_K, List[_T]] = {}
        for item in items:
            self._add_item(key_by(item), item)

    def _add_item(self, key: _K, item: _T):
        if key not in self._items:
            self._items[key] = []
        self._items[key].append(item)

    def _get_item(self, key: _K) -> _T:
        item = self._items[key].pop(0)
        self._items[key].append(item)
        return item

    def __getitem__(self, key: _K) -> _T:
        return self._get_item(key)

    def __setitem__(self, key: _K, value: _T):
        self._add_item(key, value)

    def __contains__(self, key: _K) -> bool:
        return key in self._items
