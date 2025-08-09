from vellum.workflows.nodes import BaseNode


class MyCustomNode(BaseNode):
    test: int
    changed_attribute = "original_value"
    old_attribute = "delete_this"
    _old_attribute = "keep_this"
    _test: int

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="hello")
