from dataclasses import dataclass
from typing import Optional

from vellum.workflows import BaseWorkflow
from vellum.workflows.environment import EnvironmentVariables
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


@dataclass
class ExampleCustomClass:
    field: int
    nested: Optional["ExampleCustomClass"] = None


class State(BaseState):
    value: int = 5


class Inputs(BaseInputs):
    input_value: int


class UpstreamNode(BaseNode):
    class Outputs(BaseOutputs):
        value: int

    def run(self) -> Outputs:
        return self.Outputs(value=1)


class StartNode(BaseNode):
    simple_field = Inputs.input_value
    nested_field = ExampleCustomClass(
        field=Inputs.input_value,
        nested=ExampleCustomClass(
            field=Inputs.input_value,
        ),
    )
    nested_dict_field: dict = {
        "key": Inputs.input_value,
    }
    nested_array_field = ["a", {"b": Inputs.input_value}, "c"]
    node_output_field = UpstreamNode.Outputs.value
    state_field = {"value": State.value}
    env_field = {"value": EnvironmentVariables.get("EXAMPLE_ENV_VAR")}

    class Outputs(BaseOutputs):
        simple_field: int
        nested_field: ExampleCustomClass
        super_nested_field: int
        nested_dict_field: dict
        nested_array_field: list
        node_output_field: int
        state_field: int
        env_field: str

    def run(self) -> BaseOutputs:
        if not self.nested_field.nested:
            raise ValueError("nested field is None")

        return self.Outputs(
            simple_field=self.simple_field,
            nested_field=self.nested_field,
            super_nested_field=self.nested_field.nested.field,
            nested_dict_field=self.nested_dict_field,
            nested_array_field=self.nested_array_field,
            node_output_field=self.node_output_field,
            # Nested Descriptors aren't currently caught by __get__. Needs plugin help
            # TODO: https://app.shortcut.com/vellum/story/4499
            state_field=self.state_field["value"],  # type: ignore[arg-type]
            env_field=self.env_field["value"],  # type: ignore[arg-type]
        )


class BasicNestedFieldsWorkflow(BaseWorkflow[Inputs, State]):
    graph = UpstreamNode >> StartNode

    class Outputs(BaseOutputs):
        simple_field = StartNode.Outputs.simple_field
        nested_field = StartNode.Outputs.nested_field
        super_nested_field = StartNode.Outputs.super_nested_field
        nested_dict_field = StartNode.Outputs.nested_dict_field
        nested_array_field = StartNode.Outputs.nested_array_field
        node_output_field = StartNode.Outputs.node_output_field
        state_field = StartNode.Outputs.state_field
        env_field = StartNode.Outputs.env_field
