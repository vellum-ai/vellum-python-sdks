from classifier.nodes.bot_response import BotResponse

from vellum.workflows import BaseWorkflow

from .nodes.be_happy import BeHappyPrompt
from .nodes.cheer_up import CheerUpPrompt
from .nodes.detect_tone_prompt import DetectTonePrompt
from .nodes.settle_down import SettleDownPrompt


class Workflow(BaseWorkflow):
    graph = {
        DetectTonePrompt.Ports.happy >> BeHappyPrompt,
        DetectTonePrompt.Ports.sad >> CheerUpPrompt,
        DetectTonePrompt.Ports.angry >> SettleDownPrompt,
    } >> BotResponse

    class Outputs(BaseWorkflow.Outputs):
        response = BotResponse.Outputs.value
