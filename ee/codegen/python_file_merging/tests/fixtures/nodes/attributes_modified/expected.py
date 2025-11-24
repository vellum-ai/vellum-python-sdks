from vellum.workflows import BaseNode


class MyCustomNode(BaseNode):
    test: int = None
    new_attribute_1 = "hello"
    new_attribute_2 = "world"
    changed_attribute = "new_value"
    _old_attribute = "keep_this"
    _test: int

    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="hello")
