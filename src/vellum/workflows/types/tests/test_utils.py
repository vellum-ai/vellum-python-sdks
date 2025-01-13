import pytest
from typing import Any, ClassVar, Generic, List, TypeVar, Union

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.output import OutputReference
from vellum.workflows.types.utils import get_class_attr_names, infer_types


class ExampleClass:
    alpha: str
    beta = 3
    gamma: Union[str, int]
    epsilon = OutputReference(
        name="epsilon",
        types=(List[str],),
        instance=None,
        outputs_class=BaseOutputs,
    )
    zeta: ClassVar[str]
    eta: List[str]
    kappa: Any
    mu: list[str]


T = TypeVar("T")


class ExampleGenericClass(Generic[T]):
    delta: T


class ExampleInheritedClass(ExampleClass):
    theta: int


@TryNode.wrap()
class ExampleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        iota: str


@pytest.mark.parametrize(
    "cls, attr_name, expected_type",
    [
        (ExampleClass, "alpha", (str,)),
        (ExampleClass, "beta", (int,)),
        (ExampleClass, "gamma", (str, int)),
        (ExampleGenericClass, "delta", ()),
        (ExampleGenericClass[str], "delta", (str,)),
        (ExampleClass, "epsilon", (List[str],)),
        (ExampleClass, "zeta", (str,)),
        (ExampleClass, "eta", (List[str],)),
        (ExampleInheritedClass, "theta", (int,)),
        (ExampleInheritedClass, "alpha", (str,)),
        (ExampleInheritedClass, "beta", (int,)),
        (ExampleNode.Outputs, "iota", (str,)),
        (ExampleClass, "kappa", (Any,)),
        (ExampleClass, "mu", (list[str],)),
    ],
    ids=[
        "str",
        "int",
        "str_or_int",
        "generic_blank",
        "generic_str",
        "descriptor",
        "class_var",
        "list_str",
        "inherited_int",
        "inherited_parent_annotation",
        "inherited_parent_class_var",
        "try_node_output",
        "any",
        "list_str_generic",
    ],
)
def test_infer_types(cls, attr_name, expected_type):
    assert infer_types(cls, attr_name) == expected_type


@pytest.mark.parametrize(
    "cls, expected_attr_names",
    [
        (ExampleClass, {"alpha", "beta", "gamma", "epsilon", "zeta", "eta", "kappa", "mu"}),
        (ExampleGenericClass, {"delta"}),
        (ExampleInheritedClass, {"alpha", "beta", "gamma", "epsilon", "zeta", "eta", "theta", "kappa", "mu"}),
    ],
)
def test_class_attr_names(cls, expected_attr_names):
    assert get_class_attr_names(cls) == expected_attr_names
