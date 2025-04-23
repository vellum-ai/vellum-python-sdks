from typing import Callable, Type

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import create_adornment


def test_base_adornment_node__output_references_of_same_name():
    # GIVEN a custom adornment node
    class CustomAdornmentNode(BaseAdornmentNode):
        @classmethod
        def wrap(cls) -> Callable[..., Type["CustomAdornmentNode"]]:
            return create_adornment(cls)

    # AND two nodes wrapped by the adornment with the same output
    @CustomAdornmentNode.wrap()
    class AppleNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            fruit: str

    @CustomAdornmentNode.wrap()
    class OrangeNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            fruit: str

    # WHEN get output references of these outputs
    apple_output_reference = AppleNode.Outputs.fruit
    orange_output_reference = OrangeNode.Outputs.fruit

    # THEN the output references should not be equal
    assert apple_output_reference != orange_output_reference, "Output references should not be equal"
