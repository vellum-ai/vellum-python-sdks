import pytest

from vellum.workflows.expressions.greater_than import GreaterThanExpression
from vellum.workflows.expressions.greater_than_or_equal_to import GreaterThanOrEqualToExpression
from vellum.workflows.expressions.less_than import LessThanExpression
from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
from vellum.workflows.state.base import BaseState


class Comparable:
    """A custom class with two values, where comparisons use a computed metric (multiplication)."""

    def __init__(self, value1, value2):
        self.value1 = value1  # First numerical value
        self.value2 = value2  # Second numerical value

    def computed_value(self):
        return self.value1 * self.value2  # Multiply for comparison

    def __ge__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() >= other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() >= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() > other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() > other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() <= other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() <= other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Comparable):
            return self.computed_value() < other.computed_value()
        elif isinstance(other, (int, float)):
            return self.computed_value() < other
        return NotImplemented


class NonComparable:
    """A custom class that does not support comparisons."""

    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2


class TestState(BaseState):
    pass


def test_greater_than_or_equal_to():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)  # Computed: 4 × 5 = 20
    obj2 = Comparable(2, 10)  # Computed: 2 × 10 = 20
    obj3 = Comparable(3, 6)  # Computed: 3 × 6 = 18
    obj4 = Comparable(5, 5)  # Computed: 5 × 5 = 25

    state = TestState()

    # WHEN comparing objects
    assert GreaterThanOrEqualToExpression(lhs=obj1, rhs=obj2).resolve(state) is True  # 20 >= 20
    assert GreaterThanOrEqualToExpression(lhs=obj1, rhs=obj3).resolve(state) is True  # 20 >= 18
    assert GreaterThanOrEqualToExpression(lhs=obj3, rhs=obj4).resolve(state) is False  # 18 < 25

    # WHEN comparing to raw numbers
    assert GreaterThanOrEqualToExpression(lhs=obj1, rhs=19).resolve(state) is True  # 20 >= 19
    assert GreaterThanOrEqualToExpression(lhs=obj3, rhs=20).resolve(state) is False  # 18 < 20


def test_greater_than_or_equal_to_invalid():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = "invalid"

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanOrEqualToExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>=' not supported between instances of 'Comparable' and 'str'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanOrEqualToExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>=' not supported between instances of 'str' and 'Comparable'"


def test_greater_than_or_equal_to_non_comparable():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = NonComparable(2, 10)

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanOrEqualToExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>=' not supported between instances of 'Comparable' and 'NonComparable'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanOrEqualToExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>=' not supported between instances of 'NonComparable' and 'Comparable'"


def test_greater_than():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)  # Computed: 4 × 5 = 20
    obj2 = Comparable(2, 10)  # Computed: 2 × 10 = 20
    obj3 = Comparable(3, 6)  # Computed: 3 × 6 = 18
    obj4 = Comparable(5, 5)  # Computed: 5 × 5 = 25

    state = TestState()

    # WHEN comparing objects
    assert GreaterThanExpression(lhs=obj1, rhs=obj2).resolve(state) is False  # 20 > 20
    assert GreaterThanExpression(lhs=obj1, rhs=obj3).resolve(state) is True  # 20 > 18
    assert GreaterThanExpression(lhs=obj3, rhs=obj4).resolve(state) is False  # 18 < 25

    # WHEN comparing to raw numbers
    assert GreaterThanExpression(lhs=obj1, rhs=19).resolve(state) is True  # 20 > 19
    assert GreaterThanExpression(lhs=obj3, rhs=20).resolve(state) is False  # 18 < 20


def test_greater_than_invalid():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = "invalid"

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>' not supported between instances of 'Comparable' and 'str'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>' not supported between instances of 'str' and 'Comparable'"


def test_greater_than_non_comparable():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = NonComparable(2, 10)

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>' not supported between instances of 'Comparable' and 'NonComparable'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        GreaterThanExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'>' not supported between instances of 'NonComparable' and 'Comparable'"


def test_less_than_or_equal_to():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)  # Computed: 4 × 5 = 20
    obj2 = Comparable(2, 10)  # Computed: 2 × 10 = 20
    obj3 = Comparable(3, 6)  # Computed: 3 × 6 = 18
    obj4 = Comparable(5, 5)  # Computed: 5 × 5 = 25

    state = TestState()

    # WHEN comparing objects
    assert LessThanOrEqualToExpression(lhs=obj1, rhs=obj2).resolve(state) is True  # 20 <= 20
    assert LessThanOrEqualToExpression(lhs=obj1, rhs=obj3).resolve(state) is False  # 20 > 18
    assert LessThanOrEqualToExpression(lhs=obj3, rhs=obj4).resolve(state) is True  # 18 <= 25

    # WHEN comparing to raw numbers
    assert LessThanOrEqualToExpression(lhs=obj1, rhs=21).resolve(state) is True  # 20 <= 21
    assert LessThanOrEqualToExpression(lhs=obj3, rhs=17).resolve(state) is False  # 18 > 17


def test_less_than_or_equal_to_invalid():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = "invalid"

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanOrEqualToExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<=' not supported between instances of 'Comparable' and 'str'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanOrEqualToExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<=' not supported between instances of 'str' and 'Comparable'"


def test_less_than_or_equal_to_non_comparable():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = NonComparable(2, 10)

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanOrEqualToExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<=' not supported between instances of 'Comparable' and 'NonComparable'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanOrEqualToExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<=' not supported between instances of 'NonComparable' and 'Comparable'"


def test_less_than():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)  # Computed: 4 × 5 = 20
    obj2 = Comparable(2, 10)  # Computed: 2 × 10 = 20
    obj3 = Comparable(3, 6)  # Computed: 3 × 6 = 18
    obj4 = Comparable(5, 5)  # Computed: 5 × 5 = 25

    state = TestState()

    # WHEN comparing objects
    assert LessThanExpression(lhs=obj1, rhs=obj2).resolve(state) is False  # 20 < 20
    assert LessThanExpression(lhs=obj1, rhs=obj3).resolve(state) is False  # 20 < 18
    assert LessThanExpression(lhs=obj3, rhs=obj4).resolve(state) is True  # 18 < 25

    # WHEN comparing to raw numbers
    assert LessThanExpression(lhs=obj1, rhs=21).resolve(state) is True  # 20 < 21
    assert LessThanExpression(lhs=obj3, rhs=17).resolve(state) is False  # 18 > 17


def test_less_than_invalid():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = "invalid"

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<' not supported between instances of 'Comparable' and 'str'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<' not supported between instances of 'str' and 'Comparable'"


def test_less_than_non_comparable():
    # GIVEN objects with two values
    obj1 = Comparable(4, 5)
    obj2 = NonComparable(2, 10)

    state = TestState()

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanExpression(lhs=obj1, rhs=obj2).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<' not supported between instances of 'Comparable' and 'NonComparable'"

    # WHEN comparing objects with incompatible types
    with pytest.raises(TypeError) as exc_info:
        LessThanExpression(lhs=obj2, rhs=obj1).resolve(state)

    # THEN the expected error is raised
    assert str(exc_info.value) == "'<' not supported between instances of 'NonComparable' and 'Comparable'"
