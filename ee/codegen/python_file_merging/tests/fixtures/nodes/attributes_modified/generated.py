from vellum.workflows.nodes import BaseNode


class MyCustomNode(BaseNode):
    test = None
    new_attribute_1 = "hello"
    new_attribute_2 = "world"
    changed_attribute = "new_value"

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="hello")
