from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.be_happy import BeHappyPrompt
from .nodes.bot_response import BotResponse
from .nodes.cheer_up import CheerUpPrompt
from .nodes.detect_tone_prompt import DetectTonePrompt
from .nodes.settle_down import SettleDownPrompt


class CustomPromptNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        DetectTonePrompt.Ports.happy >> BeHappyPrompt,
        DetectTonePrompt.Ports.sad >> CheerUpPrompt,
        DetectTonePrompt.Ports.angry >> SettleDownPrompt,
    } >> BotResponse

    class Outputs(BaseWorkflow.Outputs):
        response = BotResponse.Outputs.value
