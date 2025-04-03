import pytest
from uuid import UUID
from typing import Optional

from vellum.client.types.string_vellum_value_request import StringVellumValueRequest
from vellum.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.descriptors.tests.test_utils import FixtureState
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import FinalOutputNode
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState, StateMeta


def test_base_node__node_resolution__unset_pydantic_fields():
    # GIVEN a pydantic class with an optional field
    class Data(UniversalBaseModel):
        hello: str
        world: Optional[str] = None

    # AND a node that uses the pydantic class only setting one field
    my_data = Data(hello="hi")

    class MyNode(BaseNode):
        data = my_data

    # WHEN the node is initialized
    node = MyNode()

    # THEN the node is initialized with the correct data
    assert node.data.dict() == my_data.dict()


def test_base_node__node_resolution__descriptors_in_dict():
    # GIVEN an Input and State class
    class Inputs(BaseInputs):
        hello: str

    class State(BaseState):
        pass

    # AND a node referencing a descriptor in a dict
    class MyNode(BaseNode):
        data = {"world": Inputs.hello}

    # WHEN the node is initialized
    node = MyNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(hello="hi"),
            )
        )
    )

    # THEN the node is initialized with the correct data
    assert node.data["world"] == "hi"

    # AND there are inputs compiled
    assert node._inputs == {
        MyNode.data["world"]: "hi",
    }


def test_base_node__node_resolution__descriptor_in_pydantic():
    # GIVEN an Input and State class
    class Inputs(BaseInputs):
        hello: str

    class State(BaseState):
        pass

    class Data(UniversalBaseModel):
        world: str

    class MyNode(BaseNode):
        data = Data(world=Inputs.hello)

    # WHEN the node is initialized
    node = MyNode(
        state=State(
            meta=StateMeta(
                workflow_inputs=Inputs(hello="hi"),
            )
        )
    )

    # THEN the node is initialized with the correct data
    assert node.data.world == "hi"

    # AND there are inputs compiled
    assert node._inputs == {
        MyNode.data["world"]: "hi",
    }


def test_base_node__node_resolution__no_inputs():
    # GIVEN a node that defines some attributes
    class MyNode(BaseNode):
        foo = "bar"
        baz = 1

    # WHEN the node is initialized
    node = MyNode()

    # THEN the node is initialized with the correct data
    assert node.foo == "bar"
    assert node.baz == 1

    # AND there are no inputs
    assert node._inputs == {}


def test_base_node__node_resolution__coalesce_constants():
    # GIVEN a State class
    class State(BaseState):
        pass

    # AND a node that uses the coalesce operator with constants
    class FirstNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            empty: str

    class MyNode(BaseNode):
        value = FirstNode.Outputs.empty.coalesce("world")

    # WHEN the node is initialized
    node = MyNode(state=State())

    # THEN the node is initialized with the correct data
    assert node.value == "world"


def test_base_node__default_id():
    # GIVEN a node
    class MyNode(BaseNode):
        pass

    # WHEN the node is accessed
    my_id = MyNode.__id__

    # THEN it should equal the hash of `test_base_node__default_id.<locals>.MyNode`
    assert my_id == UUID("8e71bea7-ce68-492f-9abe-477c788e6273")


def test_base_node__node_resolution__descriptor_in_fern_pydantic():
    class State(BaseState):
        foo: str

    class SomeNode(BaseNode):
        model = StringVellumValueRequest(value=State.foo)

    node = SomeNode(state=State(foo="bar"))

    assert node.model.value == "bar"


def test_base_node__inherit_base_outputs():
    class MyNode(BaseNode):
        class Outputs:
            foo: str

        def run(self):
            return self.Outputs(foo="bar")  # type: ignore

    # TEST that the Outputs class is a subclass of BaseOutputs
    assert issubclass(MyNode.Outputs, BaseOutputs)

    # TEST that the Outputs class does not inherit from object
    assert object not in MyNode.Outputs.__bases__

    # TEST that the Outputs class has the correct attributes
    assert hasattr(MyNode.Outputs, "foo")

    # WHEN the node is run
    node = MyNode()
    outputs = node.run()

    # THEN the outputs should be correct
    assert outputs.foo == "bar"


def test_child_node__inherits_base_outputs_when_no_parent_outputs():
    class ParentNode(BaseNode):  # No Outputs class here
        pass

    class ChildNode(ParentNode):
        class Outputs:
            foo: str

        def run(self):
            return self.Outputs(foo="bar")  # type: ignore

    # TEST that ChildNode.Outputs is a subclass of BaseOutputs (since ParentNode has no Outputs)
    assert issubclass(ChildNode.Outputs, BaseOutputs)

    # TEST that ChildNode.Outputs has the correct attributes
    assert hasattr(ChildNode.Outputs, "foo")

    # WHEN the node is run
    node = ChildNode()
    outputs = node.run()

    # THEN the outputs should be correct
    assert outputs.foo == "bar"


def test_outputs_preserves_non_object_bases():
    class ParentNode(BaseNode):
        class Outputs:
            foo: str

    class Foo:
        bar: str

    class ChildNode(ParentNode):
        class Outputs(ParentNode.Outputs, Foo):
            pass

        def run(self):
            return self.Outputs(foo="bar", bar="baz")  # type: ignore

    # TEST that Outputs is a subclass of Foo and ParentNode.Outputs
    assert Foo in ChildNode.Outputs.__bases__, "Foo should be preserved in bases"
    assert ParentNode.Outputs in ChildNode.Outputs.__bases__, "ParentNode.Outputs should be preserved in bases"
    assert object not in ChildNode.Outputs.__bases__, "object should not be in bases"

    # TEST that Outputs has the correct attributes
    assert hasattr(ChildNode.Outputs, "foo")
    assert hasattr(ChildNode.Outputs, "bar")

    # WHEN Outputs is instantiated
    node = ChildNode()
    outputs = node.run()

    # THEN the output values should be correct
    assert outputs.foo == "bar"
    assert outputs.bar == "baz"


@pytest.mark.parametrize(
    "falsy_value,expected_type",
    [
        ("", str),
        (0, int),
    ],
)
def test_resolve_value__for_falsy_values(falsy_value, expected_type):
    """Test that falsy values in FinalOutputNode are handled correctly."""

    class FalsyOutput(FinalOutputNode[FixtureState, expected_type]):  # type: ignore
        class Outputs(FinalOutputNode.Outputs):
            value = falsy_value

    # GIVEN a node with a falsy value
    falsy_node = FalsyOutput(state=FixtureState())

    # WHEN we run the node
    falsy_output = falsy_node.run()

    # THEN the output has the correct value
    assert falsy_output.value == falsy_value
