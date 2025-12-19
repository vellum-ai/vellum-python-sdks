from pydantic import BaseModel

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs


class UserProfile(BaseModel):
    """A Pydantic model representing a user profile."""

    name: str
    age: int
    email: str


class FirstNode(BaseNode):
    """A node that outputs a Pydantic model."""

    class Outputs(BaseOutputs):
        profile: UserProfile

    def run(self) -> BaseOutputs:
        return self.Outputs(
            profile=UserProfile(
                name="Alice",
                age=30,
                email="alice@example.com",
            )
        )


class SecondNode(BaseNode):
    """A node that references a Pydantic model output and operates on its field."""

    profile = FirstNode.Outputs.profile

    class Outputs(BaseOutputs):
        greeting: str

    def run(self) -> BaseOutputs:
        return self.Outputs(greeting=f"Hello, {self.profile.name}!")


class PydanticOutputReferenceWorkflow(BaseWorkflow):
    """A workflow demonstrating Pydantic model output field references between nodes."""

    graph = FirstNode >> SecondNode

    class Outputs(BaseOutputs):
        greeting = SecondNode.Outputs.greeting
