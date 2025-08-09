from vellum.workflows.nodes import BaseNode

CONSTANT_1 = 1


class OtherClass1:
    pass


def helper_1():
    pass


class MyCustomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="hello")


CONSTANT_2 = 2


class OtherClass2:
    pass


def helper_2():
    pass
