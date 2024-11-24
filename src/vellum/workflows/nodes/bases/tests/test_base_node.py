from typing import Optional

from vellum.core.pydantic_utilities import UniversalBaseModel

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
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


def test_base_node__node_resolution__descriptor_in_dict():
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
