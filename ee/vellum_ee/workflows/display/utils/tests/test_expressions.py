import pytest

from vellum.workflows.expressions.add import AddExpression
from vellum.workflows.expressions.begins_with import BeginsWithExpression
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.concat import ConcatExpression
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
from vellum.workflows.expressions.is_error import IsErrorExpression
from vellum.workflows.expressions.is_not_null import IsNotNullExpression
from vellum.workflows.expressions.is_null import IsNullExpression
from vellum.workflows.expressions.less_than import LessThanExpression
from vellum.workflows.expressions.less_than_or_equal_to import LessThanOrEqualToExpression
from vellum.workflows.expressions.minus import MinusExpression
from vellum.workflows.expressions.not_between import NotBetweenExpression
from vellum.workflows.expressions.not_in import NotInExpression
from vellum_ee.workflows.display.utils.expressions import convert_descriptor_to_operator


def binary_expressions_with_lhs_and_rhs():
    return [
        (EqualsExpression(lhs="123", rhs="456"), "="),
        (DoesNotEqualExpression(lhs="123", rhs="456"), "!="),
        (LessThanExpression(lhs="123", rhs="456"), "<"),
        (GreaterThanExpression(lhs="123", rhs="456"), ">"),
        (LessThanOrEqualToExpression(lhs="123", rhs="456"), "<="),
        (GreaterThanOrEqualToExpression(lhs="123", rhs="456"), ">="),
        (ContainsExpression(lhs="123", rhs="456"), "contains"),
        (BeginsWithExpression(lhs="123", rhs="456"), "beginsWith"),
        (EndsWithExpression(lhs="123", rhs="456"), "endsWith"),
        (DoesNotContainExpression(lhs="123", rhs="456"), "doesNotContain"),
        (DoesNotBeginWithExpression(lhs="123", rhs="456"), "doesNotBeginWith"),
        (DoesNotEndWithExpression(lhs="123", rhs="456"), "doesNotEndWith"),
        (InExpression(lhs="123", rhs="456"), "in"),
        (NotInExpression(lhs="123", rhs="456"), "notIn"),
        (AddExpression(lhs=5, rhs=3), "+"),
        (MinusExpression(lhs=10, rhs=3), "-"),
        (ConcatExpression(lhs=[1, 2], rhs=[3, 4]), "concat"),
    ]


def unary_expressions_with_expression():
    return [
        (IsErrorExpression(expression="123"), "isError"),
        (IsNullExpression(expression="123"), "null"),
        (IsNotNullExpression(expression="123"), "notNull"),
    ]


def ternary_expressions_with_value_and_start_and_end():
    return [
        (BetweenExpression(value="123", start="456", end="789"), "between"),
        (NotBetweenExpression(value="123", start="456", end="789"), "notBetween"),
    ]


@pytest.mark.parametrize("expression, expected_operator", binary_expressions_with_lhs_and_rhs())
def test_convert_descriptor_to_operator__binary_expressions(expression, expected_operator):
    # GIVEN a binary expression descriptor
    # WHEN we convert it to an operator string
    result = convert_descriptor_to_operator(expression)

    # THEN we should get the expected operator string
    assert result == expected_operator


@pytest.mark.parametrize("expression, expected_operator", unary_expressions_with_expression())
def test_convert_descriptor_to_operator__unary_expressions(expression, expected_operator):
    # GIVEN a unary expression descriptor
    # WHEN we convert it to an operator string
    result = convert_descriptor_to_operator(expression)

    # THEN we should get the expected operator string
    assert result == expected_operator


@pytest.mark.parametrize("expression, expected_operator", ternary_expressions_with_value_and_start_and_end())
def test_convert_descriptor_to_operator__ternary_expressions(expression, expected_operator):
    # GIVEN a ternary expression descriptor
    # WHEN we convert it to an operator string
    result = convert_descriptor_to_operator(expression)

    # THEN we should get the expected operator string
    assert result == expected_operator
