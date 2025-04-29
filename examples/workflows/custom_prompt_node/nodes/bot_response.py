from classifier.nodes.be_happy import BeHappyPrompt
from classifier.nodes.cheer_up import CheerUpPrompt
from classifier.nodes.settle_down import SettleDownPrompt

from vellum.workflows.nodes.displayable import FinalOutputNode


class BotResponse(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = BeHappyPrompt.Outputs.text.coalesce(CheerUpPrompt.Outputs.text).coalesce(SettleDownPrompt.Outputs.text)
