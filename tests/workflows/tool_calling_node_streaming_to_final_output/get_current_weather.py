import math
from typing import Annotated


def get_current_weather(
    location: Annotated[str, "The location to get the weather for"], unit: Annotated[str, "The unit of temperature"]
) -> str:
    """
    Get the current weather in a given location.
    """
    return f"The current weather in {location} is sunny with a temperature of {get_temperature(70.1)} degrees {unit}."


def get_temperature(temperature: float) -> int:
    """
    Get the temperature in a given location.
    """
    return math.floor(temperature)
