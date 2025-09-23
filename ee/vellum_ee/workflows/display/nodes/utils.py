import re
from typing import Optional, TypeVar, Union, overload

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.references.node import NodeReference

_T = TypeVar("_T")


@overload
def raise_if_descriptor(node_attr: BaseDescriptor[_T]) -> _T: ...


@overload
def raise_if_descriptor(node_attr: _T) -> _T: ...


def raise_if_descriptor(node_attr: Union[NodeReference[_T], _T]) -> Optional[_T]:
    if not isinstance(node_attr, NodeReference):
        raise AttributeError(f"Expected to find a Node descriptor, but found '{node_attr.__class__.__name__}'")

    return node_attr.instance


def get_descriptor_value(node_attr: Union[NodeReference[_T], _T]) -> Optional[_T]:
    """
    Safely get the value from a node attribute that can be either a direct value or a NodeReference.

    Args:
        node_attr: The attribute value, which can be either a direct value or a NodeReference

    Returns:
        The actual value, or None if it's a NodeReference without an instance

    Raises:
        ValueError: If it's a NodeReference but the instance is None
    """
    if isinstance(node_attr, NodeReference):
        if node_attr.instance is None:
            return None
        return node_attr.instance
    return node_attr


def to_kebab_case(string: str) -> str:
    """Converts a string from Capital Case to kebab-case."""
    string = re.sub(r"(\s|_|-)+", " ", string)
    string = re.sub(
        r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
        lambda mo: " " + mo.group(0).lower(),
        string,
    )
    return "-".join(string.split())
