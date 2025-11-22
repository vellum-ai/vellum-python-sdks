from vellum.workflows import BaseState, FinalOutputNode


class TheEnd(FinalOutputNode[BaseState, list[str]]):
    class Outputs(FinalOutputNode.Outputs):
        value = ["hello", "world"]
