from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.triggers import SlackTrigger


class CheckTagNode(BaseNode[BaseState]):
    message_text = SlackTrigger.Outputs.message

    class Outputs(BaseNode.Outputs):
        is_tagged: bool
        message_text: str

    class Ports(BaseNode.Ports):
        tagged = Port.on_if(LazyReference(lambda: CheckTagNode.Outputs.is_tagged))
        not_tagged = Port.on_else()

    def run(self) -> Outputs:
        is_tagged = "apollo-oncall" in self.message_text
        return self.Outputs(is_tagged=is_tagged, message_text=self.message_text)
