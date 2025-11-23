from vellum.workflows import BaseNode


class MyCustomNode(BaseNode):
    def helper_1(self) -> str:
        pass

    class InternalClass1:
        def helper_2(self) -> str:
            pass

    def helper_3(self) -> int:
        pass

    class Outputs(BaseNode.Outputs):
        value: str

    def helper_4(self) -> str:
        pass

    class InternalClass2:
        def helper_5(self) -> str:
            pass

    def helper_6(self) -> int:
        pass

    def run(self) -> Outputs:
        return self.Outputs(value="hello")

    def helper_7(self) -> str:
        pass

    class InternalClass3:
        def helper_8(self) -> str:
            pass

    def helper_9(self) -> int:
        pass
