from collections import deque
from typing import Deque, Generic, Iterable, List, TypeVar

_T = TypeVar("_T")


class Stack(Generic[_T]):
    def __init__(self) -> None:
        self._items: Deque[_T] = deque()

    def push(self, item: _T) -> None:
        self._items.append(item)

    def extend(self, items: Iterable[_T]) -> None:
        item_list = list(items)
        for item in item_list[::-1]:
            self._items.append(item)

    def pop(self) -> _T:
        if not self.is_empty():
            return self._items.pop()
        raise IndexError("pop from empty stack")

    def peek(self) -> _T:
        if not self.is_empty():
            return self._items[-1]
        raise IndexError("peek from empty stack")

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self.dump()})"

    def dump(self) -> List[_T]:
        return [item for item in self._items][::-1]

    @classmethod
    def from_list(cls, items: List[_T]) -> "Stack[_T]":
        stack = cls()
        stack.extend(items)
        return stack

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stack):
            return False
        return self._items == other._items
