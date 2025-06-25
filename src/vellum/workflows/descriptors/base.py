from typing import TYPE_CHECKING, Any, Generic, Optional, Tuple, Type, TypeVar, Union, cast, overload

if TYPE_CHECKING:
    from vellum.workflows.expressions.accessor import AccessorExpression
    from vellum.workflows.expressions.and_ import AndExpression
    from vellum.workflows.expressions.begins_with import BeginsWithExpression
    from vellum.workflows.expressions.between import BetweenExpression
    from vellum.workflows.expressions.coalesce_expression import CoalesceExpression
    from vellum.workflows.expressions.contains import ContainsExpression
    from vellum.workflows.expressions.does_not_begin_with import DoesNotBeginWithExpression
    from vellum.workflows.expressions.does_not_contain import DoesNotContainExpression
    from vellum.workflows.expressions.does_not_end_with import DoesNotEndWithExpression
    from vellum.workflows.expressions.does_not_equal import DoesNotEqualExpression
    from vellum.workflows.expressions.ends_with import EndsWithExpression
    from vellum.workflows.expressions.equals import EqualsExpression
    from vellum.workflows.expressions.greater_than import GreaterThanExpression
    from vellum.workflows.expressions.greater_than_or_equal_to import GreaterThanOrEqualToExpression
    from vellum.workflows.expressions.in_ import InExpression
    from vellum.workflows.expressions.is_blank import IsBlankExpression
    from vellum.workflows.expressions.is_nil import IsNilExpression
    from vellum.workflows.expressions.is_not_blank import IsNotBlankExpression
    from vellum.workflows.expressions.is_not_nil import IsNotNilExpression
    from vellum.workflows.expressions.is_not_null import IsNotNullExpression
    from vellum.workflows.expressions.is_not_undefined import IsNotUndefinedExpression
    from vellum.workflows.expressions.is_null import IsNullExpression
    from vellum.workflows.expressions.is_undefined import IsUndefinedExpression
    from vellum.workflows.expressions.less_than import LessThanExpression
    from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
    from vellum.workflows.expressions.not_between import NotBetweenExpression
    from vellum.workflows.expressions.not_in import NotInExpression
    from vellum.workflows.expressions.or_ import OrExpression
    from vellum.workflows.expressions.parse_json import ParseJsonExpression
    from vellum.workflows.nodes.bases import BaseNode
    from vellum.workflows.state.base import BaseState

_T = TypeVar("_T", covariant=True)
_O = TypeVar("_O")
_O2 = TypeVar("_O2")


class BaseDescriptor(Generic[_T]):
    _name: str
    _types: Tuple[Type[_T], ...]
    _instance: Optional[_T]

    def __init__(self, *, name: str, types: Tuple[Type[_T], ...], instance: Optional[_T] = None) -> None:
        self._name = name
        self._types = types
        self._instance = instance

    @property
    def name(self) -> str:
        return self._name

    @property
    def types(self) -> Tuple[Type[_T], ...]:
        return self._types

    @property
    def instance(self) -> Optional[_T]:
        return self._instance

    def resolve(self, state: "BaseState") -> _T:
        raise NotImplementedError("Descriptor must implement resolve method")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._name == other._name

    def __hash__(self) -> int:
        return hash(self._name)

    def __repr__(self) -> str:
        return self._name

    @overload
    def __get__(self, instance: "BaseNode", owner: Type["BaseNode"]) -> _T: ...

    @overload
    def __get__(self, instance: Any, owner: Optional[Type]) -> "BaseDescriptor[_T]": ...

    def __get__(self, instance: Any, owner: Optional[Type]) -> Union["BaseDescriptor[_T]", _T]:
        if not instance:
            return self

        if instance.__class__.__name__ == "BaseNode":
            node = cast("BaseNode", instance)
            return self.resolve(node.state)

        return self

    # TODO: We should figure out how to remove these dynamic imports
    # https://app.shortcut.com/vellum/story/4504
    @overload
    def __or__(self, other: "BaseDescriptor[_O]") -> "OrExpression[_T, _O]": ...

    @overload
    def __or__(self, other: _O) -> "OrExpression[_T, _O]": ...

    def __or__(self, other: "Union[BaseDescriptor[_O], _O]") -> "OrExpression[_T, _O]":
        from vellum.workflows.expressions.or_ import OrExpression

        return OrExpression(lhs=self, rhs=other)

    @overload
    def __and__(self, other: "BaseDescriptor[_O]") -> "AndExpression[_T, _O]": ...

    @overload
    def __and__(self, other: _O) -> "AndExpression[_T, _O]": ...

    def __and__(self, other: "Union[BaseDescriptor[_O], _O]") -> "AndExpression[_T, _O]":
        from vellum.workflows.expressions.and_ import AndExpression

        return AndExpression(lhs=self, rhs=other)

    @overload
    def coalesce(self, other: "BaseDescriptor[_O]") -> "CoalesceExpression[_T, _O]": ...

    @overload
    def coalesce(self, other: _O) -> "CoalesceExpression[_T, _O]": ...

    def coalesce(self, other: "Union[BaseDescriptor[_O], _O]") -> "CoalesceExpression[_T, _O]":
        from vellum.workflows.expressions.coalesce_expression import CoalesceExpression

        return CoalesceExpression(lhs=self, rhs=other)

    def __getitem__(self, field: Union[str, int]) -> "AccessorExpression":
        from vellum.workflows.expressions.accessor import AccessorExpression

        return AccessorExpression(base=self, field=field)

    @overload
    def equals(self, other: "BaseDescriptor[_O]") -> "EqualsExpression[_T, _O]": ...

    @overload
    def equals(self, other: _O) -> "EqualsExpression[_T, _O]": ...

    def equals(self, other: "Union[BaseDescriptor[_O], _O]") -> "EqualsExpression[_T, _O]":
        from vellum.workflows.expressions.equals import EqualsExpression

        return EqualsExpression(lhs=self, rhs=other)

    @overload
    def does_not_equal(self, other: "BaseDescriptor[_O]") -> "DoesNotEqualExpression[_T, _O]": ...

    @overload
    def does_not_equal(self, other: _O) -> "DoesNotEqualExpression[_T, _O]": ...

    def does_not_equal(self, other: "Union[BaseDescriptor[_O], _O]") -> "DoesNotEqualExpression[_T, _O]":
        from vellum.workflows.expressions.does_not_equal import DoesNotEqualExpression

        return DoesNotEqualExpression(lhs=self, rhs=other)

    @overload
    def less_than(self, other: "BaseDescriptor[_O]") -> "LessThanExpression[_T, _O]": ...

    @overload
    def less_than(self, other: _O) -> "LessThanExpression[_T, _O]": ...

    def less_than(self, other: "Union[BaseDescriptor[_O], _O]") -> "LessThanExpression[_T, _O]":
        from vellum.workflows.expressions.less_than import LessThanExpression

        return LessThanExpression(lhs=self, rhs=other)

    @overload
    def greater_than(self, other: "BaseDescriptor[_O]") -> "GreaterThanExpression[_T, _O]": ...

    @overload
    def greater_than(self, other: _O) -> "GreaterThanExpression[_T, _O]": ...

    def greater_than(self, other: "Union[BaseDescriptor[_O], _O]") -> "GreaterThanExpression[_T, _O]":
        from vellum.workflows.expressions.greater_than import GreaterThanExpression

        return GreaterThanExpression(lhs=self, rhs=other)

    @overload
    def less_than_or_equal_to(self, other: "BaseDescriptor[_O]") -> "LessThanOrEqualToExpression[_T, _O]": ...

    @overload
    def less_than_or_equal_to(self, other: _O) -> "LessThanOrEqualToExpression[_T, _O]": ...

    def less_than_or_equal_to(self, other: "Union[BaseDescriptor[_O], _O]") -> "LessThanOrEqualToExpression[_T, _O]":
        from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression

        return LessThanOrEqualToExpression(lhs=self, rhs=other)

    @overload
    def greater_than_or_equal_to(self, other: "BaseDescriptor[_O]") -> "GreaterThanOrEqualToExpression[_T, _O]": ...

    @overload
    def greater_than_or_equal_to(self, other: _O) -> "GreaterThanOrEqualToExpression[_T, _O]": ...

    def greater_than_or_equal_to(
        self, other: "Union[BaseDescriptor[_O], _O]"
    ) -> "GreaterThanOrEqualToExpression[_T, _O]":
        from vellum.workflows.expressions.greater_than_or_equal_to import GreaterThanOrEqualToExpression

        return GreaterThanOrEqualToExpression(lhs=self, rhs=other)

    @overload
    def contains(self, other: "BaseDescriptor[_O]") -> "ContainsExpression[_T, _O]": ...

    @overload
    def contains(self, other: _O) -> "ContainsExpression[_T, _O]": ...

    def contains(self, other: "Union[BaseDescriptor[_O], _O]") -> "ContainsExpression[_T, _O]":
        from vellum.workflows.expressions.contains import ContainsExpression

        return ContainsExpression(lhs=self, rhs=other)

    @overload
    def begins_with(self, other: "BaseDescriptor[_O]") -> "BeginsWithExpression[_T, _O]": ...

    @overload
    def begins_with(self, other: _O) -> "BeginsWithExpression[_T, _O]": ...

    def begins_with(self, other: "Union[BaseDescriptor[_O], _O]") -> "BeginsWithExpression[_T, _O]":
        from vellum.workflows.expressions.begins_with import BeginsWithExpression

        return BeginsWithExpression(lhs=self, rhs=other)

    @overload
    def ends_with(self, other: "BaseDescriptor[_O]") -> "EndsWithExpression[_T, _O]": ...

    @overload
    def ends_with(self, other: _O) -> "EndsWithExpression[_T, _O]": ...

    def ends_with(self, other: "Union[BaseDescriptor[_O], _O]") -> "EndsWithExpression[_T, _O]":
        from vellum.workflows.expressions.ends_with import EndsWithExpression

        return EndsWithExpression(lhs=self, rhs=other)

    @overload
    def does_not_contain(self, other: "BaseDescriptor[_O]") -> "DoesNotContainExpression[_T, _O]": ...

    @overload
    def does_not_contain(self, other: _O) -> "DoesNotContainExpression[_T, _O]": ...

    def does_not_contain(self, other: "Union[BaseDescriptor[_O], _O]") -> "DoesNotContainExpression[_T, _O]":
        from vellum.workflows.expressions.does_not_contain import DoesNotContainExpression

        return DoesNotContainExpression(lhs=self, rhs=other)

    @overload
    def does_not_begin_with(self, other: "BaseDescriptor[_O]") -> "DoesNotBeginWithExpression[_T, _O]": ...

    @overload
    def does_not_begin_with(self, other: _O) -> "DoesNotBeginWithExpression[_T, _O]": ...

    def does_not_begin_with(self, other: "Union[BaseDescriptor[_O], _O]") -> "DoesNotBeginWithExpression[_T, _O]":
        from vellum.workflows.expressions.does_not_begin_with import DoesNotBeginWithExpression

        return DoesNotBeginWithExpression(lhs=self, rhs=other)

    @overload
    def does_not_end_with(self, other: "BaseDescriptor[_O]") -> "DoesNotEndWithExpression[_T, _O]": ...

    @overload
    def does_not_end_with(self, other: _O) -> "DoesNotEndWithExpression[_T, _O]": ...

    def does_not_end_with(self, other: "Union[BaseDescriptor[_O], _O]") -> "DoesNotEndWithExpression[_T, _O]":
        from vellum.workflows.expressions.does_not_end_with import DoesNotEndWithExpression

        return DoesNotEndWithExpression(lhs=self, rhs=other)

    def is_null(self) -> "IsNullExpression":
        from vellum.workflows.expressions.is_null import IsNullExpression

        return IsNullExpression(expression=self)

    def is_not_null(self) -> "IsNotNullExpression":
        from vellum.workflows.expressions.is_not_null import IsNotNullExpression

        return IsNotNullExpression(expression=self)

    def is_nil(self) -> "IsNilExpression":
        from vellum.workflows.expressions.is_nil import IsNilExpression

        return IsNilExpression(expression=self)

    def is_not_nil(self) -> "IsNotNilExpression":
        from vellum.workflows.expressions.is_not_nil import IsNotNilExpression

        return IsNotNilExpression(expression=self)

    def is_undefined(self) -> "IsUndefinedExpression":
        from vellum.workflows.expressions.is_undefined import IsUndefinedExpression

        return IsUndefinedExpression(expression=self)

    def is_not_undefined(self) -> "IsNotUndefinedExpression":
        from vellum.workflows.expressions.is_not_undefined import IsNotUndefinedExpression

        return IsNotUndefinedExpression(expression=self)

    @overload
    def in_(self, other: "BaseDescriptor[_O]") -> "InExpression[_T, _O]": ...

    @overload
    def in_(self, other: _O) -> "InExpression[_T, _O]": ...

    def in_(self, other: "Union[BaseDescriptor[_O], _O]") -> "InExpression[_T, _O]":
        from vellum.workflows.expressions.in_ import InExpression

        return InExpression(lhs=self, rhs=other)

    @overload
    def not_in(self, other: "BaseDescriptor[_O]") -> "NotInExpression[_T, _O]": ...

    @overload
    def not_in(self, other: _O) -> "NotInExpression[_T, _O]": ...

    def not_in(self, other: "Union[BaseDescriptor[_O], _O]") -> "NotInExpression[_T, _O]":
        from vellum.workflows.expressions.not_in import NotInExpression

        return NotInExpression(lhs=self, rhs=other)

    @overload
    def between(self, start: "BaseDescriptor[_O]", end: "BaseDescriptor[_O2]") -> "BetweenExpression[_T, _O, _O2]": ...

    @overload
    def between(self, start: _O, end: _O2) -> "BetweenExpression[_T, _O, _O2]": ...

    def between(
        self, start: "Union[BaseDescriptor[_O], _O]", end: "Union[BaseDescriptor[_O2], _O2]"
    ) -> "BetweenExpression[_T, _O, _O2]":
        from vellum.workflows.expressions.between import BetweenExpression

        return BetweenExpression(value=self, start=start, end=end)

    @overload
    def not_between(
        self, start: "BaseDescriptor[_O]", end: "BaseDescriptor[_O2]"
    ) -> "NotBetweenExpression[_T, _O, _O2]": ...

    @overload
    def not_between(self, start: _O, end: _O2) -> "NotBetweenExpression[_T, _O, _O2]": ...

    def not_between(
        self, start: "Union[BaseDescriptor[_O], _O]", end: "Union[BaseDescriptor[_O2], _O2]"
    ) -> "NotBetweenExpression[_T, _O, _O2]":
        from vellum.workflows.expressions.not_between import NotBetweenExpression

        return NotBetweenExpression(value=self, start=start, end=end)

    def is_blank(self) -> "IsBlankExpression":
        from vellum.workflows.expressions.is_blank import IsBlankExpression

        return IsBlankExpression(expression=self)

    def is_not_blank(self) -> "IsNotBlankExpression":
        from vellum.workflows.expressions.is_not_blank import IsNotBlankExpression

        return IsNotBlankExpression(expression=self)

    def parse_json(self) -> "ParseJsonExpression[_T]":
        from vellum.workflows.expressions.parse_json import ParseJsonExpression

        return ParseJsonExpression(expression=self)
