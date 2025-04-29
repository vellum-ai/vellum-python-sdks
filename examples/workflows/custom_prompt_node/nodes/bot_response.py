from vellum.workflows.nodes.displayable import FinalOutputNode

from .be_happy import BeHappyPrompt
from .cheer_up import CheerUpPrompt
from .settle_down import SettleDownPrompt


class BotResponse(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = BeHappyPrompt.Outputs.text.coalesce(CheerUpPrompt.Outputs.text).coalesce(SettleDownPrompt.Outputs.text)
