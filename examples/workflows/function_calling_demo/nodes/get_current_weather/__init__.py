from typing import Any

from vellum.client.types import CodeExecutionPackage
from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.references import VellumSecretReference
from vellum.workflows.state import BaseState

from ..parse_function_call import ParseFunctionCall


class GetCurrentWeather(CodeExecutionNode[BaseState, Any]):
    filepath = "./script.py"
    code_inputs = {
        "kwargs": ParseFunctionCall.Outputs.function_args,
        "gmaps_api_key": VellumSecretReference("GOOGLE_GEOCODING_API_KEY"),
        "openweather_api_key": VellumSecretReference("OPEN_WEATHER_API_KEY"),
    }
    runtime = "PYTHON_3_11_6"
    packages = [
        CodeExecutionPackage(name="googlemaps", version="4.10.0"),
        CodeExecutionPackage(name="requests", version="2.32.3"),
    ]
